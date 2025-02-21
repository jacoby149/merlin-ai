
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tarfile
import io
import os
# Initialize the Docker client from the host's Docker socket.
import docker
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import settings
import re

# settings
import os as os_lib
TARGET_API = 'api'
TARGET_UI = 'ui'
TARGET_API_SELF='ai-api-self'
# goes through the above config variables 
# checks if env vars of those names exist and sets them if they do
vars = [v for v in globals()]
for v in vars :
    env_val = os_lib.getenv(v)
    if env_val == None:
        continue
    else:
        globals()[v] = env_val

app = FastAPI(title="ChatGPT-like API with Router")
# Include the chat router.

app.add_middleware(
        
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the chat router.

# You can also define additional routers or endpoints here.

"""
    COMMANDS
"""

client = docker.from_env()

# Create a router instance.
cmd_router = APIRouter(prefix="/commands", tags=["commands"])

@cmd_router.post("/container_restart_ui")
async def container_restart_ui():
    """
    Restarts the entire UI container using the Docker SDK. The container is located
    by filtering on the Docker Compose service label "ui", and then restarted using
    the Docker API. Note: since this endpoint runs inside the container, the connection
    may drop when the container stops.
    """
    try:
        # Locate the UI container using its Docker Compose service label.
        containers = client.containers.list(filters={"label": f"com.docker.compose.service={TARGET_UI}"})
        if not containers:
            raise HTTPException(status_code=404, detail="UI container not found")
        container = containers[0]
        
        container.restart(timeout=10)
        # Restart the container.
        
        return {"message": "UI container restarted"}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error restarting UI container: {e}")

@cmd_router.post("/container_restart_api")
async def container_restart_api():
    """
    Restarts the entire API container using the Docker SDK. The container is located
    by filtering on the Docker Compose service label "api", and then restarted using
    the Docker API. Note: since this endpoint runs inside the container, the connection
    may drop when the container stops.
    """
    try:
        # Find the container by the Docker Compose service label.
        containers = client.containers.list(filters={"label": f"com.docker.compose.service={TARGET_API}"})
        if not containers:
            raise HTTPException(status_code=404, detail="API container not found")
        container = containers[0]
        
        # Restart the container.
        container.restart(timeout=10)
        
        return {"message": "API container restarted"}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error restarting API container: {e}")

class Package(BaseModel):
    name: str

@cmd_router.post("/install_restart_api")
async def install_restart_api(pkg: Package=Package(name="pandas")):
    """
    Installs the specified package into the API container's pipenv environment by executing
    a pipenv install command inside the container. After installation, it calls the existing
    container_restart_api() endpoint to restart the API container.
    """
    # Locate the API container using its Docker Compose service label.
    containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
    if not containers:
        raise HTTPException(status_code=404, detail="API container not found")
    container = containers[0]

    # Execute pipenv install inside the API container.
    try:
        exit_code, output = container.exec_run(cmd=["pipenv", "install", pkg.name])
        if exit_code != 0:
            error_output = output.decode('utf-8') if isinstance(output, bytes) else output
            raise HTTPException(status_code=500, detail=f"Error installing package: {error_output}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during pipenv install in API container: {e}")

    # Call the already defined container_restart_api() endpoint to restart the API container.
    return await container_restart_api()

@cmd_router.post("/install_restart_ui")
async def install_restart_ui(pkg: Package=Package(name="react-chartjs-2")):
    """
    Installs the specified npm package into the UI container's environment by executing
    an npm install command inside the container. After installation, it calls the already
    defined container_restart_ui() endpoint to restart the UI container.
    """
    # Locate the UI container using its Docker Compose service label.
    containers = client.containers.list(filters={"label":  f"com.docker.compose.service={TARGET_UI}"})
    if not containers:
        raise HTTPException(status_code=404, detail="UI container not found")
    container = containers[0]

    # Execute npm install inside the UI container.
    try:
        exit_code, output = container.exec_run(cmd=["npm", "install", pkg.name])
        if exit_code != 0:
            error_output = output.decode('utf-8') if isinstance(output, bytes) else output
            raise HTTPException(status_code=500, detail=f"Error installing package: {error_output}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during npm install in UI container: {e}")

    # Reuse the existing container_restart_ui() endpoint to restart the UI container.
    return await container_restart_ui()

@cmd_router.get("/tail_ui_logs")
async def scan_ui(num_lines: int = 10):
    """
    Returns the last num_lines of logs from the UI container by querying
    the host's Docker daemon using the Docker Compose service label.
    """
    try:
        # Filter containers by the Docker Compose service label.
        containers = client.containers.list(filters={"label": f"com.docker.compose.service={TARGET_UI}"})
        if not containers:
            raise HTTPException(status_code=404, detail="UI service container not found")
        
        # If there are multiple containers for the service, select the first one.
        container = containers[0]
        logs = container.logs(tail=num_lines).decode('utf-8')
        return {"logs": logs}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching UI logs: {e}")


@cmd_router.get("/tail_api_logs")
async def scan_api(num_lines: int = 10):
    """
    Returns the last num_lines of logs from the API container by querying
    the host's Docker daemon using the Docker Compose service label.
    """
    try:
        # Filter containers by the Docker Compose service label.
        containers = client.containers.list(filters={"label": f"com.docker.compose.service={TARGET_API}"})
        if not containers:
            raise HTTPException(status_code=404, detail="API service container not found")
        
        # If there are multiple containers for the service, select the first one.
        container = containers[0]
        logs = container.logs(tail=num_lines).decode('utf-8')
        return {"logs": logs}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching API logs: {e}")


class Service(str, Enum):
    ui = "ui"
    api = "api"

class ReadFilePayload(BaseModel):
    service: Service
    path: str


@cmd_router.get("/read")
async def read_file(payload:ReadFilePayload):
    """
    Reads the content of a file from a container.
    
    Query parameters:
      - service: the Docker Compose service name (e.g., 'api' or 'ui')
      - path: the absolute path of the file in the container (e.g., '/app/main.py')
    """
    client = docker.from_env()
    containers = client.containers.list(filters={"label": f"com.docker.compose.service={payload.service.value}"})
    if not containers:
        raise HTTPException(status_code=404, detail=f"{payload.service.value} container not found")
    container = containers[0]

    try:
        # Get the archive for the specified file.
        stream, stat = container.get_archive(payload.path)
        file_bytes = b"".join(stream)
        file_like_object = io.BytesIO(file_bytes)
        with tarfile.open(fileobj=file_like_object, mode="r:*") as tar:
            names = tar.getnames()
            # Try to match the expected file (using its basename) if possible.
            base_name = os.path.basename(payload.path)
            if base_name in names:
                member = tar.getmember(base_name)
            elif names:
                # Fallback: use the first file found.
                member = tar.getmember(names[0])
            else:
                raise HTTPException(status_code=500, detail="No files found in tar archive")
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise HTTPException(status_code=500, detail="Error extracting file from archive")
            content = file_obj.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file from {payload.service.value} container: {e}")

    return {"content": content}

class WriteFilePayload(BaseModel):
    service: Service
    path: str
    content: str

@cmd_router.post("/write")
async def write_file(payload: WriteFilePayload):
    """
    Overwrites a file in a container with new content.
    
    Payload:
      - service: the Docker Compose service name (e.g., 'api' or 'ui')
      - path: the absolute path of the file in the container (e.g., '/app/main.py')
      - content: the new content for the file.
    """
    client = docker.from_env()
    containers = client.containers.list(filters={"label": f"com.docker.compose.service={payload.service.value}"})
    if not containers:
        raise HTTPException(status_code=404, detail=f"{payload.service.value} container not found")
    container = containers[0]

    # Split the given path into directory and file name.
    directory = os.path.dirname(payload.path)
    file_name = os.path.basename(payload.path)

    # Create an in-memory tar archive containing the new file.
    data = payload.content.encode("utf-8")
    tarstream = io.BytesIO()
    with tarfile.open(fileobj=tarstream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name=file_name)
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))
    tarstream.seek(0)

    try:
        success = container.put_archive(path=directory, data=tarstream.getvalue())
        if not success:
            raise HTTPException(status_code=500, detail="Error writing file to container")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file upload: {e}")
    await container_restart_api()
    return {"message": f"File '{payload.path}' updated in {payload.service.value} container"}

MAIN_PY = "app/main.py"
APP_JS = "app/src/App.js"
APP_CSS = "app/src/App.css"

@cmd_router.post("/write_main_py")
async def write_main_py(content:str):
    """
    Overwrites the main.py file inside the API container's /app directory with the new content provided.
    The new main.py content is sent in the request payload. After updating the file, it calls the 
    container_restart_api() endpoint to restart the API container.
    """
    return await write_file(WriteFilePayload(service=TARGET_API,path=MAIN_PY,content=content))

@cmd_router.post("/write_app_js")
async def write_app_js(content: str):
    """
    Overwrites the src/App.js file inside the UI container's /app directory with the new content provided.
    The new src/App.js content is sent in the request payload. After updating the file, it calls the 
    container_restart_ui() endpoint to restart the UI container.
    """
    return await write_file(WriteFilePayload(service=TARGET_UI,path=APP_JS,content=content))

@cmd_router.post("/write_app_css")
async def write_app_css(content:str):
    """
    Overwrites the src/App.css file inside the UI container's /app directory with the new content provided.
    After updating the file, it calls the container_restart_ui() endpoint to restart the UI container.
    """
    return await write_file(WriteFilePayload(service=TARGET_UI,path=APP_CSS,content=content))


@cmd_router.get("/read_app_css")
async def read_app_css():
    """
    Reads the content of src/App.css from the UI container's /app directory and returns it.
    """
    return await read_file(ReadFilePayload(service=TARGET_UI,path=APP_CSS))

@cmd_router.get("/read_app_js")
async def read_app_js():
    """
    Reads the content of src/App.js from the UI container's /app directory and returns it.
    """
    return await read_file(ReadFilePayload(service=TARGET_UI,path=APP_JS))


@cmd_router.get("/read_main_py")
async def read_main_py():
    """
    Reads the content of main.py from the API container's /app directory and returns it.
    """
    return await read_file(ReadFilePayload(service=TARGET_API,path=MAIN_PY))

class NewMainContent(BaseModel):
    content: str

"""
    AUTO CODER
"""



# Create a router instance.
auto_router = APIRouter(prefix="/auto_coder", tags=["auto_coder"])

# Initialize the OpenAI client.
client = OpenAI(api_key=settings.OPENAPI_KEY)

if not client.api_key:
    raise Exception("Missing OpenAI API key. Please set the OPENAPI_API_KEY environment variable.")


import re
from fastapi import HTTPException

def ask_api(prompt: str):
    """
    Sends the prompt to the GPT-4o mini model and extracts the modified code
    (enclosed between <|start-code|> and <|end-code|>) and any additional explanatory reply.
    """
    conversation_history = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or any available model
            messages=conversation_history,
            temperature=0.5,      # adjust as needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {e}")

    full_response = response.choices[0].message.content

    # Use a regex to find the text enclosed in our custom tokens.
    pattern = r"<\|start-code\|>(.*?)<\|end-code\|>"
    match = re.search(pattern, full_response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        # Remove the code block from the full response to form the reply text.
        reply_text = re.sub(pattern, '', full_response, flags=re.DOTALL).strip()
    else:
        code_block = ""
        reply_text = full_response.strip()

    return code_block, reply_text

class ModRequest(BaseModel):
    chat:str
    context:str

class ModRespose(BaseModel):
    reply:str

@auto_router.post("/api_mod")
async def api_mod(r:ModRequest):
    """
    Modifies the main.py file
    """
    preface = "Here is a main.py for a fastapi implementation!"
    main_py = await read_main_py()
    main_py = main_py["content"]
    chat = r.chat
    code = "Answer with a modified version of main.py surrounded by <|start-code|> and <|end-code|>. the output is being written right over the file!!!!"
    exp = "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes!"
    prompt = "\n".join([preface,main_py,chat,code,exp])
    code,reply = ask_api(prompt)
    await write_main_py(code)
    return {"reply":reply}


def ask_ui(prompt: str):
    """
    Sends the prompt to the GPT-4o mini model and extracts the modified code
    (enclosed between <|start-code|> and <|end-code|>) and any additional explanatory reply.
    """
    conversation_history = [{"role": "user", "content": prompt}]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or any available model
            messages=conversation_history,
            temperature=0.5,      # adjust as needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {e}")

    full_response = response.choices[0].message.content

    # Use a regex to find the text enclosed in our custom tokens.
    pattern = r"<\|start-code\|>(.*?)<\|end-code\|>"
    match = re.search(pattern, full_response, re.DOTALL)
    if match:
        code_block = match.group(1).strip()
        # Remove the code block from the full response to form the reply text.
        reply_text = re.sub(pattern, '', full_response, flags=re.DOTALL).strip()
    else:
        code_block = ""
        reply_text = full_response.strip()

    return code_block, reply_text


@auto_router.post("/ui_mod")
async def ui_mod(r:ModRequest):
    """
    Modifies the App.js file
    """
    api_preface="Here is a main.py for a fastapi implementation. it is hosted on port 8000"
    main_py = await read_main_py()
    main_py = main_py["content"]
 
    preface = "Here is a App.js for a React implementation!"
    app_js = await read_app_js()
    app_js = app_js["content"]

    chat = r.chat
    code = "Answer with a modified version of App.js surrounded by <|start-code|> and <|end-code|>. the output is being written right over the file!!!!"
    exp = "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes!"
    prompt = "\n".join([api_preface,main_py,preface,app_js,chat,code,exp])
    code,reply = ask_ui(prompt)
    await write_app_js(code)
    return {"reply":reply}

@auto_router.post("/fs_mod")
async def fs_mod(r:ModRequest):
    api_reply = (await api_mod(r))["reply"]
    ui_reply = (await ui_mod(r))["reply"]
    return {"reply":f"API : {api_reply} \n UI : {ui_reply}"}

app.include_router(cmd_router)
app.include_router(auto_router)


