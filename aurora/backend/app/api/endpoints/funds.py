from app.modules.data_loader import load_available_funds
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_funds():
    result = load_available_funds()

    return result
