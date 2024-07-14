from fastapi import APIRouter

from app.api.routes import backtest, expected_returns, funds, health, optimisation, risk_models

api_router = APIRouter()

api_router.include_router(funds.router, tags=["funds"], prefix="/funds")
api_router.include_router(backtest.router, tags=["backtest"], prefix="/backtest")
api_router.include_router(expected_returns.router, tags=["optimisation"], prefix="/optimisation")
api_router.include_router(risk_models.router, tags=["optimisation"], prefix="/optimisation")
api_router.include_router(optimisation.router, tags=["optimisation"], prefix="/optimisation")
api_router.include_router(health.router, tags=["healthchecks"])
