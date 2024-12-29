"""Healthcheck APIRouter."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", status_code=200)
async def health() -> dict[str, str]:
    """Basic health check. Can't use healthz on google cloud."""
    return {"status": "ok"}
