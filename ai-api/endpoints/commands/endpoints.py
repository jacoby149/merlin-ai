"""
    commands.py
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import tarfile
import io
import settings

# Initialize the Docker client from the host's Docker socket.
import docker
client = docker.from_env()


# Create a router instance.
router = APIRouter(prefix="/commands", tags=["commands"])

@router.post("/container_restart_ui")
async def container_restart_ui():
    """
    Restarts the entire UI container using the Docker SDK. The container is located
    by filtering on the Docker Compose service label "ui", and then restarted using
    the Docker API. Note: since this endpoint runs inside the container, the connection
    may drop when the container stops.
    """
    try:
        # Locate the UI container using its Docker Compose service label.
        containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
        if not containers:
            raise HTTPException(status_code=404, detail="UI container not found")
        container = containers[0]
        
        # Restart the container.
        container.restart(timeout=10)
        
        return {"message": "UI container restarted"}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=f"Error restarting UI container: {e}")

@router.post("/container_restart_api")
async def container_restart_api():
    """
    Restarts the entire API container using the Docker SDK. The container is located
    by filtering on the Docker Compose service label "api", and then restarted using
    the Docker API. Note: since this endpoint runs inside the container, the connection
    may drop when the container stops.
    """
    try:
        # Find the container by the Docker Compose service label.
        containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
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

@router.post("/install_restart_api")
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

@router.post("/install_restart_ui")
async def install_restart_ui(pkg: Package=Package(name="react-chartjs-2")):
    """
    Installs the specified npm package into the UI container's environment by executing
    an npm install command inside the container. After installation, it calls the already
    defined container_restart_ui() endpoint to restart the UI container.
    """
    # Locate the UI container using its Docker Compose service label.
    containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
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

class NewMainContent(BaseModel):
    content: str


@router.post("/write_api")
async def write_api(new_main: NewMainContent):
    """
    Overwrites the main.py file inside the API container's /app directory with the new content provided.
    The new main.py content is sent in the request payload. After updating the file, it calls the 
    container_restart_api() endpoint to restart the API container.
    """
    # Locate the API container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
    if not containers:
        raise HTTPException(status_code=404, detail="API container not found")
    container = containers[0]

    # Create an in-memory tar archive containing the new main.py file.
    data = new_main.content.encode("utf-8")
    tarstream = io.BytesIO()
    with tarfile.open(fileobj=tarstream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name="main.py")
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))
    tarstream.seek(0)

    # Use put_archive to overwrite the main.py file in the /app directory.
    try:
        success = container.put_archive(path="/app", data=tarstream.getvalue())
        if not success:
            raise HTTPException(status_code=500, detail="Error writing main.py to the API container")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file upload: {e}")

    # Call the existing container_restart_api() endpoint to restart the API container.
    return await container_restart_api()

class NewAppContent(BaseModel):
    content: str

@router.post("/write_ui")
async def write_ui(new_app: NewAppContent):
    """
    Overwrites the src/App.js file inside the UI container's /app directory with the new content provided.
    The new src/App.js content is sent in the request payload. After updating the file, it calls the 
    container_restart_ui() endpoint to restart the UI container.
    """
    # Locate the UI container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
    if not containers:
        raise HTTPException(status_code=404, detail="UI container not found")
    container = containers[0]

    # Create an in-memory tar archive containing the new src/App.js file.
    data = new_app.content.encode("utf-8")
    tarstream = io.BytesIO()
    with tarfile.open(fileobj=tarstream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name="src/App.js")
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))
    tarstream.seek(0)

    # Use put_archive to overwrite the src/App.js file in the /app directory.
    try:
        success = container.put_archive(path="/app", data=tarstream.getvalue())
        if not success:
            raise HTTPException(status_code=500, detail="Error writing src/App.js to the UI container")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file upload: {e}")


class NewStyleContent(BaseModel):
    content: str

@router.post("/write_ui_style")
async def write_ui_style(new_style: NewStyleContent):
    """
    Overwrites the src/App.css file inside the UI container's /app directory with the new content provided.
    After updating the file, it calls the container_restart_ui() endpoint to restart the UI container.
    """
    # Locate the UI container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
    if not containers:
        raise HTTPException(status_code=404, detail="UI container not found")
    container = containers[0]

    # Create an in-memory tar archive containing the new src/App.css file.
    data = new_style.content.encode("utf-8")
    tarstream = io.BytesIO()
    with tarfile.open(fileobj=tarstream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name="src/App.css")
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))
    tarstream.seek(0)

    # Use put_archive to overwrite the src/App.css file in the /app directory.
    try:
        success = container.put_archive(path="/app", data=tarstream.getvalue())
        if not success:
            raise HTTPException(status_code=500, detail="Error writing src/App.css to the UI container")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file upload: {e}")

    # Reuse the existing container_restart_ui() endpoint to restart the UI container.
    return await container_restart_ui()

@router.get("/read_ui_style")
async def read_ui_style():
    """
    Reads the content of src/App.css from the UI container's /app directory and returns it.
    """
    # Locate the UI container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
    if not containers:
        raise HTTPException(status_code=404, detail="UI container not found")
    container = containers[0]

    try:
        # Get the archive for the file /app/src/App.css
        stream, stat = container.get_archive("/app/src/App.css")
        file_bytes = b"".join(stream)
        file_like_object = io.BytesIO(file_bytes)
        # Open the tar archive.
        with tarfile.open(fileobj=file_like_object, mode="r:*") as tar:
            # List all file names in the tar archive.
            names = tar.getnames()
            # Try to locate the expected file name.
            if "src/App.css" in names:
                member = tar.getmember("src/App.css")
            elif names:
                # Fallback: use the first file in the archive.
                member = tar.getmember(names[0])
            else:
                raise HTTPException(status_code=500, detail="No files found in tar archive")
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise HTTPException(status_code=500, detail="Error extracting file from archive")
            content = file_obj.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading src/App.css from UI container: {e}")

    return {"content": content}

@router.get("/read_ui")
async def read_ui():
    """
    Reads the content of src/App.js from the UI container's /app directory and returns it.
    """
    # Locate the UI container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=ui"})
    if not containers:
        raise HTTPException(status_code=404, detail="UI container not found")
    container = containers[0]

    try:
        # Get the archive for the file /app/src/App.js.
        stream, stat = container.get_archive("/app/src/App.js")
        file_bytes = b"".join(stream)
        file_like_object = io.BytesIO(file_bytes)
        # Open the tar archive.
        with tarfile.open(fileobj=file_like_object, mode="r:*") as tar:
            names = tar.getnames()
            # Try to locate the expected file name.
            if "src/App.js" in names:
                member = tar.getmember("src/App.js")
            elif names:
                # Fallback: use the first file in the archive.
                member = tar.getmember(names[0])
            else:
                raise HTTPException(status_code=500, detail="No files found in tar archive")
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise HTTPException(status_code=500, detail="Error extracting file from archive")
            content = file_obj.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading src/App.js from UI container: {e}")

    return {"content": content}

@router.get("/read_api")
async def read_api():
    """
    Reads the content of main.py from the API container's /app directory and returns it.
    """
    # Locate the API container using its Docker Compose service label.
    client = docker.from_env()
    containers = client.containers.list(filters={"label": "com.docker.compose.service=api"})
    if not containers:
        raise HTTPException(status_code=404, detail="API container not found")
    container = containers[0]

    try:
        # Get the archive for the file /app/main.py.
        stream, stat = container.get_archive("/app/main.py")
        file_bytes = b"".join(stream)
        file_like_object = io.BytesIO(file_bytes)
        # Open the tar archive.
        with tarfile.open(fileobj=file_like_object, mode="r:*") as tar:
            names = tar.getnames()
            # Try to locate "main.py" or fallback to the first file in the archive.
            if "main.py" in names:
                member = tar.getmember("main.py")
            elif names:
                member = tar.getmember(names[0])
            else:
                raise HTTPException(status_code=500, detail="No files found in tar archive")
            file_obj = tar.extractfile(member)
            if file_obj is None:
                raise HTTPException(status_code=500, detail="Error extracting file from archive")
            content = file_obj.read().decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading main.py from API container: {e}")

    return {"content": content}
