import re

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

import settings
from routers.commands import (
    APP_JS,
    MAIN_PY,
    read_file_from_service,
    write_file_to_service,
)


router = APIRouter(prefix="/auto_coder", tags=["auto_coder"])


class ModRequest(BaseModel):
    chat: str
    context: str = ""


class ModResponse(BaseModel):
    reply: str


def get_ai_client() -> OpenAI:
    api_key = settings.OPENAI_API_KEY.get_secret_value()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing OpenAI API key. Please set OPENAI_API_KEY or OPENAPI_KEY.",
        )

    return OpenAI(api_key=api_key, base_url=settings.OPENAI_API_BASE_URL)


def ask_model(prompt: str, temperature: float | None = None) -> tuple[str, str]:
    request_kwargs = {
        "model": settings.AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    if temperature is not None:
        request_kwargs["temperature"] = temperature

    try:
        response = get_ai_client().chat.completions.create(**request_kwargs)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {exc}")

    full_response = response.choices[0].message.content or ""
    pattern = r"<\|start-code\|>(.*?)<\|end-code\|>"
    match = re.search(pattern, full_response, re.DOTALL)

    if not match:
        return "", full_response.strip()

    code_block = match.group(1).strip()
    reply_text = re.sub(pattern, "", full_response, flags=re.DOTALL).strip()
    return code_block, reply_text


def build_prompt(*parts: str) -> str:
    return "\n".join(part for part in parts if part)


@router.post("/api_mod", response_model=ModResponse)
async def api_mod(request: ModRequest) -> dict[str, str]:
    main_py = read_file_from_service(settings.TARGET_API, MAIN_PY)

    prompt = build_prompt(
        "Here is a main.py for a FastAPI implementation!",
        main_py,
        request.context,
        request.chat,
        "Answer with the full modified version of main.py surrounded by <|start-code|> and <|end-code|>. The output is being written right over the file.",
        "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes.",
    )
    code, reply = ask_model(prompt)

    write_file_to_service(settings.TARGET_API, MAIN_PY, code, restart=True)
    return {"reply": reply}


@router.post("/ui_mod", response_model=ModResponse)
async def ui_mod(request: ModRequest) -> dict[str, str]:
    main_py = read_file_from_service(settings.TARGET_API, MAIN_PY)
    app_js = read_file_from_service(settings.TARGET_UI, APP_JS)

    prompt = build_prompt(
        "Here is a main.py for a FastAPI implementation. It is hosted on port 8000.",
        main_py,
        "Here is an App.js for a React implementation!",
        app_js,
        request.context,
        request.chat,
        "Answer with a modified version of App.js surrounded by <|start-code|> and <|end-code|>. The output is being written right over the file.",
        "Anything in the reply not encapsulated in <|start-code|> and <|end-code|> will be shown to a user to explain the changes.",
    )
    code, reply = ask_model(prompt, temperature=0.5)

    write_file_to_service(settings.TARGET_UI, APP_JS, code, restart=True)
    return {"reply": reply}


@router.post("/fs_mod", response_model=ModResponse)
async def fs_mod(request: ModRequest) -> dict[str, str]:
    api_reply = (await api_mod(request))["reply"]
    ui_reply = (await ui_mod(request))["reply"]
    return {"reply": f"API : {api_reply} \n UI : {ui_reply}"}
