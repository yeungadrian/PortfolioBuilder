from fastapi import APIRouter

router = APIRouter()


@router.get("/ping/")
def ping() -> str:
    """
    Simple ping check.

    Returns
    -------
    str
        pong
    """
    return "pong"
