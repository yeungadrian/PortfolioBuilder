from fastapi import APIRouter

from app.api.routes import funds, health

api_router = APIRouter()

api_router.include_router(funds.router, tags=["funds"], prefix="/funds")
api_router.include_router(health.router, tags=["healthchecks"])
