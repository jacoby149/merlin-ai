"""
    commands.py
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import settings
import subprocess

# Initialize the Docker client from the host's Docker socket.
import docker
client = docker.from_env()


# Create a router instance.
router = APIRouter(prefix="/commands", tags=["commands"])

@router.post("/container_restart_ui")
async def container_restart_ui():
    """
    Restarts the UI container by invoking:
    docker restart ui
    """
    try:
        result = subprocess.run(
            ["docker", "restart", "ui"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"message": "UI container restarted", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error restarting UI container: {e.stderr}")

@router.post("/container_restart_api")
async def container_restart_api():
    """
    Restarts the API container by invoking:
    docker restart api
    """
    try:
        result = subprocess.run(
            ["docker", "restart", "api"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"message": "API container restarted", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error restarting API container: {e.stderr}")


# ----- In-Container Process Restart Endpoints -----

@router.post("/restart_ui")
async def restart_ui():
    """
    Restarts the React app running inside the UI container.
    It first kills the process (using pkill on the npm/react process) and then re-launches it with npm start.
    """
    try:
        # Attempt to kill the running React process. Ignore errors if no matching process is found.
        subprocess.run(
            ["docker", "exec", "ui", "pkill", "-f", "npm"],
            capture_output=True,
            text=True
        )
        # Start the React app in detached mode
        result = subprocess.run(
            ["docker", "exec", "-d", "ui", "npm", "start"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"message": "React app in UI container restarted", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error restarting React app: {e.stderr}")


@router.post("/restart_api")
async def restart_api():
    """
    Restarts the FastAPI (uvicorn) process in the API container without stopping the container.
    It finds the container by the Docker Compose service label, kills any running uvicorn process,
    and then starts a new one in detached mode.
    """
    try:
        # Locate the container using the Docker Compose service label.
        containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
        if not containers:
            raise HTTPException(status_code=404, detail="API container not found")
        container = containers[0]

        # Kill any running uvicorn process. This command might return a non-zero exit code if no process is found.
        kill_result = container.exec_run(["pkill", "-f", "uvicorn"], stdout=True, stderr=True)
        # (Optional) You can log kill_result.output if needed.

        # Start the FastAPI server using uvicorn in detached mode.
        # Adjust the command as needed based on your container's setup.
        container.exec_run(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            detach=True
        )

        return {"message": "FastAPI (uvicorn) restarted in API container"}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error restarting FastAPI: {e}")

# ----- Log Scanning Endpoints -----

@router.get("/tail_ui_logs")
async def scan_ui(num_lines: int = 10):
    """
    Returns the last num_lines of logs from the UI container by querying
    the host's Docker daemon using the Docker Compose service label.
    """
    try:
        # Filter containers by the Docker Compose service label.
        containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
        if not containers:
            raise HTTPException(status_code=404, detail="UI service container not found")
        
        # If there are multiple containers for the service, select the first one.
        container = containers[0]
        logs = container.logs(tail=num_lines).decode('utf-8')
        return {"logs": logs}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching UI logs: {e}")


@router.get("/tail_api_logs")
async def scan_api(num_lines: int = 10):
    """
    Returns the last num_lines of logs from the API container by querying
    the host's Docker daemon using the Docker Compose service label.
    """
    try:
        # Filter containers by the Docker Compose service label.
        containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
        if not containers:
            raise HTTPException(status_code=404, detail="API service container not found")
        
        # If there are multiple containers for the service, select the first one.
        container = containers[0]
        logs = container.logs(tail=num_lines).decode('utf-8')
        return {"logs": logs}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching API logs: {e}")
