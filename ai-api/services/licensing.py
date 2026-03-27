import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException

import settings
from gumroad_validate import GumroadValidationNetworkError, verify_gumroad_license, verify_merlin_license


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_license_state_path() -> Path:
    path = Path(settings.LICENSE_STATE_FILE)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path
    return path


def default_license_state() -> dict[str, Any]:
    return {
        "activated": False,
        "license_key": None,
        "product_id": None,
        "product_name": None,
        "last_validated_at": None,
        "last_validation_error": None,
        "purchase": None,
    }


def load_license_state() -> dict[str, Any]:
    path = get_license_state_path()
    if not path.exists():
        return default_license_state()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default_license_state()

    return {**default_license_state(), **data}


def save_license_state(state: dict[str, Any]) -> dict[str, Any]:
    path = get_license_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    try:
        path.chmod(0o600)
    except Exception:
        pass

    return state


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def should_refresh(state: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or utc_now()
    last_validated_at = parse_timestamp(state.get("last_validated_at"))
    if last_validated_at is None:
        return True

    elapsed = now - last_validated_at
    return elapsed.total_seconds() >= settings.LICENSE_REFRESH_INTERVAL_SECONDS


def within_grace_window(state: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or utc_now()
    last_validated_at = parse_timestamp(state.get("last_validated_at"))
    if last_validated_at is None:
        return False

    elapsed = now - last_validated_at
    return elapsed.total_seconds() <= settings.LICENSE_GRACE_WINDOW_SECONDS


def build_public_license_status(state: dict[str, Any]) -> dict[str, Any]:
    last_validated_at = parse_timestamp(state.get("last_validated_at"))
    next_refresh_at = None
    grace_expires_at = None

    if last_validated_at is not None:
        next_refresh_at = (
            last_validated_at + timedelta(seconds=settings.LICENSE_REFRESH_INTERVAL_SECONDS)
        ).isoformat()
        grace_expires_at = (
            last_validated_at + timedelta(seconds=settings.LICENSE_GRACE_WINDOW_SECONDS)
        ).isoformat()

    purchase = state.get("purchase") or {}

    return {
        "activated": bool(state.get("activated")),
        "product_name": state.get("product_name"),
        "product_id": state.get("product_id"),
        "purchase_email": purchase.get("email"),
        "purchase_name": purchase.get("full_name") or purchase.get("name"),
        "last_validated_at": state.get("last_validated_at"),
        "next_refresh_at": next_refresh_at,
        "grace_expires_at": grace_expires_at,
        "last_validation_error": state.get("last_validation_error"),
        "refresh_interval_seconds": settings.LICENSE_REFRESH_INTERVAL_SECONDS,
        "grace_window_seconds": settings.LICENSE_GRACE_WINDOW_SECONDS,
        "license_state_file": str(get_license_state_path()),
    }


def mark_license_invalid(state: dict[str, Any], reason: str) -> dict[str, Any]:
    state.update(
        {
            "activated": False,
            "last_validation_error": reason,
        }
    )
    return save_license_state(state)


def activate_license(license_key: str) -> dict[str, Any]:
    normalized_key = license_key.strip()
    if not normalized_key:
        raise HTTPException(status_code=400, detail="License key is required")

    try:
        result = verify_merlin_license(normalized_key)
    except GumroadValidationNetworkError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach Gumroad during activation: {exc}",
        )

    if result.get("success") is not True:
        raise HTTPException(status_code=400, detail="Invalid Gumroad license key")

    now = utc_now().isoformat()
    state = save_license_state(
        {
            "activated": True,
            "license_key": normalized_key,
            "product_id": result.get("merlin_product_id"),
            "product_name": result.get("merlin_product_name"),
            "last_validated_at": now,
            "last_validation_error": None,
            "purchase": result.get("purchase"),
        }
    )
    return state


def ensure_activated_license() -> dict[str, Any]:
    now = utc_now()
    state = load_license_state()

    if not state.get("activated") or not state.get("license_key"):
        raise HTTPException(status_code=403, detail="Activation required. Call /activate first.")

    if not should_refresh(state, now=now):
        return state

    product_id = state.get("product_id")
    if not product_id:
        raise HTTPException(
            status_code=403,
            detail="Stored activation is incomplete. Re-activate with /activate.",
        )

    try:
        result = verify_gumroad_license(
            product_id,
            state["license_key"],
            timeout=settings.GUMROAD_REQUEST_TIMEOUT_SECONDS,
        )
    except GumroadValidationNetworkError as exc:
        if within_grace_window(state, now=now):
            state["last_validation_error"] = f"Gumroad unavailable; using grace window: {exc}"
            save_license_state(state)
            return state

        raise HTTPException(
            status_code=503,
            detail="License revalidation failed and grace window expired.",
        )

    if result.get("success") is not True:
        mark_license_invalid(state, "Gumroad rejected stored license key")
        raise HTTPException(status_code=403, detail="Stored license is no longer valid.")

    state.update(
        {
            "activated": True,
            "last_validated_at": now.isoformat(),
            "last_validation_error": None,
            "purchase": result.get("purchase") or state.get("purchase"),
        }
    )
    save_license_state(state)
    return state


def require_activated_license() -> dict[str, Any]:
    return ensure_activated_license()
