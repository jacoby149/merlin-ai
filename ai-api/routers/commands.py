import io
import os
import tarfile
from typing import Optional

import docker
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import settings


router = APIRouter(
    prefix="/commands",
    tags=["commands 🔒 activation required"],
    responses={403: {"description": "Activated Gumroad license required. Call /activate first."}},
)

MAIN_PY = "/app/main.py"
APP_JS = "/app/src/App.js"
APP_CSS = "/app/src/App.css"


def get_docker_client() -> docker.DockerClient:
    return docker.from_env()


def get_service_container(service: str):
    try:
        containers = get_docker_client().containers.list(
            filters={"label": f"com.docker.compose.service={service}"}
        )
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Docker connection error: {exc}")

    if not containers:
        raise HTTPException(status_code=404, detail=f"{service} container not found")

    return containers[0]


def restart_service_container(service: str, timeout: int = 10) -> None:
    container = get_service_container(service)

    try:
        container.restart(timeout=timeout)
    except docker.errors.DockerException as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error restarting {service} container: {exc}",
        )


def read_file_from_service(service: str, path: str) -> str:
    container = get_service_container(service)

    try:
        stream, _ = container.get_archive(path)
        file_bytes = b"".join(stream)
        file_like_object = io.BytesIO(file_bytes)

        with tarfile.open(fileobj=file_like_object, mode="r:*") as archive:
            names = archive.getnames()
            if not names:
                raise HTTPException(status_code=500, detail="No files found in tar archive")

            base_name = os.path.basename(path)
            member_name = next(
                (name for name in names if os.path.basename(name) == base_name),
                names[0],
            )
            member = archive.getmember(member_name)
            file_obj = archive.extractfile(member)
            if file_obj is None:
                raise HTTPException(
                    status_code=500,
                    detail="Error extracting file from archive",
                )

            return file_obj.read().decode("utf-8")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading file from {service} container: {exc}",
        )


def write_file_to_service(service: str, path: str, content: str, restart: bool = False) -> None:
    container = get_service_container(service)

    directory = os.path.dirname(path) or "/"
    file_name = os.path.basename(path)
    data = content.encode("utf-8")
    tarstream = io.BytesIO()

    with tarfile.open(fileobj=tarstream, mode="w") as archive:
        tarinfo = tarfile.TarInfo(name=file_name)
        tarinfo.size = len(data)
        archive.addfile(tarinfo, io.BytesIO(data))

    tarstream.seek(0)

    try:
        success = container.put_archive(path=directory, data=tarstream.getvalue())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during file upload: {exc}")

    if not success:
        raise HTTPException(status_code=500, detail="Error writing file to container")

    if restart:
        restart_service_container(service)


class Package(BaseModel):
    name: str


class ReadFilePayload(BaseModel):
    service: str
    path: str


class WriteFilePayload(BaseModel):
    service: str
    path: str
    content: str


class GitCommitPayload(BaseModel):
    message: str
    author_name: Optional[str] = settings.GIT_NAME
    author_email: Optional[str] = settings.GIT_EMAIL


@router.post("/container_restart_ui")
async def container_restart_ui() -> dict[str, str]:
    restart_service_container(settings.TARGET_UI)
    return {"message": "UI container restarted"}


@router.post("/container_restart_api")
async def container_restart_api() -> dict[str, str]:
    restart_service_container(settings.TARGET_API)
    return {"message": "API container restarted"}


@router.post("/install_restart_api")
async def install_restart_api(pkg: Package = Package(name="pandas")) -> dict[str, str]:
    container = get_service_container(settings.TARGET_API)

    try:
        exit_code, output = container.exec_run(cmd=["uv", "add", pkg.name])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error during uv add in API container: {exc}",
        )

    if exit_code != 0:
        error_output = output.decode("utf-8") if isinstance(output, bytes) else output
        raise HTTPException(status_code=500, detail=f"Error installing package: {error_output}")

    restart_service_container(settings.TARGET_API)
    return {"message": "API container restarted"}


@router.post("/install_restart_ui")
async def install_restart_ui(
    pkg: Package = Package(name="react-chartjs-2"),
) -> dict[str, str]:
    container = get_service_container(settings.TARGET_UI)

    try:
        exit_code, output = container.exec_run(cmd=["npm", "install", pkg.name])
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error during npm install in UI container: {exc}",
        )

    if exit_code != 0:
        error_output = output.decode("utf-8") if isinstance(output, bytes) else output
        raise HTTPException(status_code=500, detail=f"Error installing package: {error_output}")

    restart_service_container(settings.TARGET_UI)
    return {"message": "UI container restarted"}


@router.get("/tail_ui_logs")
async def tail_ui_logs(num_lines: int = 10) -> dict[str, str]:
    container = get_service_container(settings.TARGET_UI)

    try:
        logs = container.logs(tail=num_lines).decode("utf-8")
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching UI logs: {exc}")

    return {"logs": logs}


@router.get("/tail_api_logs")
async def tail_api_logs(num_lines: int = 10) -> dict[str, str]:
    container = get_service_container(settings.TARGET_API)

    try:
        logs = container.logs(tail=num_lines).decode("utf-8")
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching API logs: {exc}")

    return {"logs": logs}


@router.get("/read")
async def read_file(payload: ReadFilePayload) -> dict[str, str]:
    return {"content": read_file_from_service(payload.service, payload.path)}


@router.post("/write")
async def write_file(payload: WriteFilePayload) -> dict[str, str]:
    write_file_to_service(
        service=payload.service,
        path=payload.path,
        content=payload.content,
        restart=True,
    )
    return {"message": f"File '{payload.path}' updated in {payload.service} container"}


@router.post("/write_main_py")
async def write_main_py(content: str) -> dict[str, str]:
    write_file_to_service(settings.TARGET_API, MAIN_PY, content, restart=True)
    return {"message": f"File '{MAIN_PY}' updated in {settings.TARGET_API} container"}


@router.post("/write_app_js")
async def write_app_js(content: str) -> dict[str, str]:
    write_file_to_service(settings.TARGET_UI, APP_JS, content, restart=True)
    return {"message": f"File '{APP_JS}' updated in {settings.TARGET_UI} container"}


@router.post("/write_app_css")
async def write_app_css(content: str) -> dict[str, str]:
    write_file_to_service(settings.TARGET_UI, APP_CSS, content, restart=True)
    return {"message": f"File '{APP_CSS}' updated in {settings.TARGET_UI} container"}


@router.get("/read_app_css")
async def read_app_css() -> dict[str, str]:
    return {"content": read_file_from_service(settings.TARGET_UI, APP_CSS)}


@router.get("/read_app_js")
async def read_app_js() -> dict[str, str]:
    return {"content": read_file_from_service(settings.TARGET_UI, APP_JS)}


@router.get("/read_main_py")
async def read_main_py() -> dict[str, str]:
    return {"content": read_file_from_service(settings.TARGET_API, MAIN_PY)}


@router.post("/git_commit")
async def git_commit(payload: GitCommitPayload) -> dict[str, str]:
    container = get_service_container("git-controller")

    try:
        exit_code, _ = container.exec_run(
            cmd=["git", "config", "user.email", payload.author_email or ""]
        )
        if exit_code != 0:
            raise HTTPException(status_code=500, detail="Failed to set user email")

        exit_code, _ = container.exec_run(
            cmd=["git", "config", "user.name", payload.author_name or ""]
        )
        if exit_code != 0:
            raise HTTPException(status_code=500, detail="Failed to set user name")

        exit_code, output = container.exec_run(
            cmd=["git", "commit", "-a", "-m", payload.message]
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during git operations: {exc}")

    if exit_code != 0:
        error_output = output.decode("utf-8") if isinstance(output, bytes) else output
        raise HTTPException(status_code=500, detail=f"Error making git commit: {error_output}")

    return {"message": f"Git commit made with message: '{payload.message}'"}


@router.post("/undo")
async def undo_commit() -> dict[str, str]:
    container = get_service_container("git-controller")

    try:
        exit_code, output = container.exec_run(cmd=["git", "checkout", "HEAD^"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during git undo operation: {exc}")

    if exit_code != 0:
        error_output = output.decode("utf-8") if isinstance(output, bytes) else output
        raise HTTPException(
            status_code=500,
            detail=f"Error checking out to previous commit: {error_output}",
        )

    return {"message": "Checked out to previous commit"}


@router.post("/redo")
async def redo_commit() -> dict[str, str]:
    container = get_service_container("git-controller")

    try:
        exit_code, output = container.exec_run(cmd=["git", "checkout", "HEAD@{1}"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during git redo operation: {exc}")

    if exit_code != 0:
        error_output = output.decode("utf-8") if isinstance(output, bytes) else output
        raise HTTPException(
            status_code=500,
            detail=f"Error checking out to next commit: {error_output}",
        )

    return {"message": "Checked out to next commit"}
