import os
import sys
import boto3
import uvicorn
import signal
import threading
import time
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Capture original environment for local .env overrides
original_env = dict(os.environ)

# Peak declarative mapping
DEFAULT_SECRETS_MAP = {
    "OPENAI_API_KEY": "/merlinai/api/openai_api_key",
    "GEMINI_API_KEY": "/merlinai/api/gemini_api_key",
    "ANTHROPIC_API_KEY": "/merlinai/api/anthropic_api_key"
}

# In-memory shared file path (Never touches the physical hard drive)
SHARED_MEM_FILE = "/dev/shm/opencode_env.json"

class LaunchConfig(BaseModel):
    secrets_mapping: Dict[str, str]

@app.get("/")
def config_page():
    json_str = json.dumps(DEFAULT_SECRETS_MAP, indent=4)
    
    return HTMLResponse(f"""
        <html>
            <head>
                <style>
                    body {{ font-family: system-ui, sans-serif; background: #1e1e2e; color: #cdd6f4; padding: 40px; display: flex; flex-direction: column; align-items: center; }}
                    h1 {{ color: #89b4fa; margin-bottom: 5px; }}
                    p {{ color: #a6adc8; margin-bottom: 20px; }}
                    .container {{ background: #181825; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); width: 100%; max-width: 600px; }}
                    textarea {{ width: 100%; height: 200px; background: #11111b; color: #a6e3a1; border: 1px solid #313244; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 14px; margin-bottom: 20px; box-sizing: border-box; }}
                    button {{ width: 100%; padding: 15px; font-size: 16px; font-weight: bold; cursor: pointer; background: #89b4fa; color: #11111b; border: none; border-radius: 8px; transition: 0.2s; }}
                    button:hover {{ background: #b4befe; }}
                    button:disabled {{ background: #45475a; cursor: not-allowed; }}
                    #status {{ margin-top: 20px; text-align: center; font-weight: bold; color: #f9e2af; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>OpenCode Bootstrapper</h1>
                    <p>Map your environment variables to AWS Parameter Store paths.</p>
                    
                    <textarea id="json-input">{json_str}</textarea>
                    
                    <button id="launch-btn" onclick="launch()">Launch OpenCode</button>
                    <div id="status"></div>
                </div>

                <script>
                    async function launch() {{
                        const btn = document.getElementById('launch-btn');
                        const status = document.getElementById('status');
                        let mapping = {{}};
                        
                        try {{
                            mapping = JSON.parse(document.getElementById('json-input').value);
                        }} catch (e) {{
                            status.innerText = "Invalid JSON format!";
                            status.style.color = "#f38ba8";
                            return;
                        }}

                        btn.innerText = "Booting...";
                        btn.disabled = true;
                        status.innerText = "Fetching secrets from AWS...";
                        status.style.color = "#89dceb";

                        try {{
                            const res = await fetch('/launch/aws', {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{secrets_mapping: mapping}})
                            }});
                            
                            const data = await res.json();
                            
                            if (data.error) {{
                                status.innerText = data.error;
                                status.style.color = "#f38ba8";
                                btn.innerText = "Launch OpenCode";
                                btn.disabled = false;
                            }} else {{
                                status.innerText = data.message;
                                status.style.color = "#a6e3a1";
                                setTimeout(() => {{ window.location.reload(); }}, 4000);
                            }}
                        }} catch (e) {{
                            status.innerText = "Network Error.";
                            btn.disabled = false;
                        }}
                    }}
                </script>
            </body>
        </html>
    """)

@app.post("/launch/aws")
def launch_aws(config: LaunchConfig):
    mapping = config.secrets_mapping
    ssm_paths = list(set(mapping.values()))
    
    fetched_secrets = {}
    final_env_vars = {}

    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        ssm = boto3.client('ssm', region_name=region)
        
        for i in range(0, len(ssm_paths), 10):
            chunk = ssm_paths[i:i+10]
            response = ssm.get_parameters(Names=chunk, WithDecryption=True)
            for param in response.get('Parameters', []):
                fetched_secrets[param['Name']] = param['Value']
                
        for env_var, ssm_path in mapping.items():
            if ssm_path in fetched_secrets:
                final_env_vars[env_var] = fetched_secrets[ssm_path]
                
            env_val = original_env.get(env_var)
            if env_val is not None:
                final_env_vars[env_var] = env_val
                
    except Exception as e:
        return {"error": f"Failed to fetch keys: {str(e)}"}

    # Write secrets to Linux Shared Memory (/dev/shm) 
    with open(SHARED_MEM_FILE, "w") as f:
        json.dump(final_env_vars, f)

    def shutdown():
        time.sleep(1)
        # Find the Master process PID and send it the shutdown signal
        master_pid = os.getppid()
        print(f"\n[Worker] Keys fetched! Sending shutdown to Master (PID {master_pid})...", flush=True)
        os.kill(master_pid, signal.SIGINT)
        
    threading.Thread(target=shutdown).start()
    return {"message": "Success! Handing off process to OpenCode..."}

if __name__ == "__main__":
    print(f"\n--- Starting Bootstrapper Master Process (PID: {os.getpid()}) ---", flush=True)
    
    try:
        # reload=True spawns a master process and child workers.
        uvicorn.run("bootstrapper:app", host="0.0.0.0", port=4096, reload=True)
    except BaseException as e:
        # This catches Uvicorn's internal sys.exit(0) and prevents the container from dying!
        print(f"\n[Master] Caught Uvicorn exit signal.", flush=True)
        pass 
        
    print("[Master] Uvicorn stopped. Checking for handoff file...", flush=True)
    
    # --- POST-SHUTDOWN HANDOFF (Runs strictly in the Master Process) ---
    
    if os.path.exists(SHARED_MEM_FILE):
        print("[Master] Handoff file found! Port 4096 released.", flush=True)
        
        # 1. Read the securely fetched secrets
        with open(SHARED_MEM_FILE, "r") as f:
            new_env = json.load(f)
            
        # 2. Immediately delete the in-memory file
        os.remove(SHARED_MEM_FILE)
        
        # 3. Apply them to the Master process environment
        for k, v in new_env.items():
            os.environ[k] = v
            print(f"[Master] Injected securely: {k}", flush=True)
            
        print("\n>>> Molding process into OpenCode... <<<", flush=True)
        
        # 4. Morph entirely into OpenCode
        cmd = ["opencode", "serve", "--hostname", "0.0.0.0", "--port", "4096"]
        
        # Flush buffers to ensure all logs print before we destroy the Python interpreter
        sys.stdout.flush()
        sys.stderr.flush()
        
        try:
            os.execvp(cmd[0], cmd)
        except Exception as e:
            print(f"[ERROR] Failed to execute OpenCode: {e}", flush=True)
    else:
        print("[Master] No handoff file found. Exiting normally.", flush=True)
