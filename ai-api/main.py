from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import settings
from routers.auto_coder import router as auto_coder_router
from routers.commands import router as commands_router
from routers.licensing import router as licensing_router
from services.licensing import require_activated_license


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(licensing_router)
app.include_router(commands_router, dependencies=[Depends(require_activated_license)])
app.include_router(auto_coder_router, dependencies=[Depends(require_activated_license)])


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    html = Path(__file__).with_name("linktree.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get(
    "/health",
    dependencies=[Depends(require_activated_license)],
    responses={403: {"description": "Activated Gumroad license required. Call /activate first."}},
)
def health() -> dict[str, str]:
    return {
        "service": settings.APP_NAME,
        "target_api": settings.TARGET_API,
        "target_ui": settings.TARGET_UI,
        "model": settings.AI_MODEL,
    }
