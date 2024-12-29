"""FastAPI routers."""

from fastapi import APIRouter

from app.api.routes import backtest, health, optimisation, securities

api_router = APIRouter()

api_router.include_router(securities.router, tags=["securities"], prefix="/securities")
api_router.include_router(backtest.router, tags=["backtest"], prefix="/backtest")
api_router.include_router(optimisation.router, tags=["optimisation"], prefix="/optimisation")
api_router.include_router(health.router, tags=["healthchecks"])
