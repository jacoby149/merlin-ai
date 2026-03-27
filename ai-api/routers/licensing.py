from fastapi import APIRouter
from pydantic import BaseModel

from services.licensing import activate_license, build_public_license_status, load_license_state


router = APIRouter(tags=["licensing"])


class ActivationRequest(BaseModel):
    license_key: str


@router.post("/activate")
async def activate(payload: ActivationRequest) -> dict[str, object]:
    state = activate_license(payload.license_key)
    return {
        "message": "License activated successfully",
        "license": build_public_license_status(state),
    }


@router.get("/activation/status")
async def activation_status() -> dict[str, object]:
    return build_public_license_status(load_license_state())
