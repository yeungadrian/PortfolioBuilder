from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", status_code=200)
async def healthz() -> dict[str, str]:
    """
    Basic health check.

    Returns a 200 OK response if the application is running.
    """
    return {"status": "ok"}
