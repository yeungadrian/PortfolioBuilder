from fastapi import APIRouter

from app.api.routes import backtest, funds, health, optimisation

api_router = APIRouter()

api_router.include_router(funds.router, tags=["funds"], prefix="/funds")
api_router.include_router(backtest.router, tags=["backtest"], prefix="/backtest")
api_router.include_router(optimisation.router, tags=["optimisation"], prefix="/optimisation")
api_router.include_router(health.router, tags=["healthchecks"])
