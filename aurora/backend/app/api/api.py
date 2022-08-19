from app.api.endpoints import backtest, factor, frontier, funds
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(backtest.router, prefix="/backtest")
api_router.include_router(funds.router, prefix="/funds")
api_router.include_router(factor.router, prefix="/factorRegression")
api_router.include_router(frontier.router, prefix="/portfolioOptimisation")
