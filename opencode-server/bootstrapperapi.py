import os
import sys
import boto3
import uvicorn
import signal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Global flag to track if we should boot OpenCode after the web server stops
system_state = {"launch_opencode": False}

@app.get("/")
def config_page():
    # A simple UI. You can make this as complex as you want later!
    return HTMLResponse("""
        <html>
            <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                <h1>OpenCode Setup</h1>
                <p>Select your secret provider to inject keys into memory and launch.</p>
                <form action="/launch/aws" method="post">
                    <button style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                        Fetch Keys from AWS & Launch OpenCode
                    </button>
                </form>
            </body>
        </html>
    """)

@app.post("/launch/aws")
def launch_aws():
    print("Fetching API keys from AWS Parameter Store...", flush=True)
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        ssm = boto3.client('ssm', region_name=region)
        response = ssm.get_parameters_by_path(Path='/merlinai/api/', WithDecryption=True)
        
        for param in response.get('Parameters', []):
            key_name = param['Name'].split('/')[-1].upper()
            os.environ[key_name] = param['Value']
            print(f"Loaded: {key_name}", flush=True)
            
    except Exception as e:
        return {"error": f"Failed to fetch keys: {str(e)}"}

    # 1. Set the flag so the script knows to launch OpenCode
    system_state["launch_opencode"] = True
    
    # 2. Send a graceful shutdown signal to Uvicorn
    # This ensures Uvicorn sends the HTTP response to the browser before dying
    os.kill(os.getpid(), signal.SIGINT)

    return {"message": "Success! Secrets loaded. OpenCode is starting... Please wait 5 seconds and refresh this page."}

if __name__ == "__main__":
    print("Starting Bootstrapper UI on port 4096...", flush=True)
    
    # Start the FastAPI server (this blocks until the server shuts down)
    uvicorn.run(app, host="0.0.0.0", port=4096)
    
    # --- The code below only runs AFTER FastAPI has shut down ---
    
    if system_state["launch_opencode"]:
        print("FastAPI shutdown complete. Port 4096 released.", flush=True)
        print("Replacing process with OpenCode...", flush=True)
        
        # Define the exact OpenCode command
        cmd = ["opencode", "serve", "--hostname", "0.0.0.0", "--port", "4096"]
        
        # os.execvp completely overwrites this Python process with OpenCode.
        # OpenCode inherits os.environ (which now contains our AWS secrets!)
        os.execvp(cmd[0], cmd)
