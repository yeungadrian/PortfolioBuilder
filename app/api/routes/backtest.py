"""Backtesting related endpoints."""

import polars as pl
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import BacktestResult, BacktestScenario, Holding, PortfolioValue
from app.portfolio_analysis.backtest import run_backtesting
from app.portfolio_analysis.metrics import get_portfolio_metrics

router = APIRouter()


def get_invalid_ids(ids: list[str]) -> list[str]:
    """Validate ids provided."""
    available_ids = (
        pl.scan_parquet(settings.security_details).filter(pl.col("id").is_in(ids)).collect()["id"].to_list()
    )
    not_available = [_id for _id in ids if _id not in available_ids]
    return not_available


@router.post("")
def backtest_portfolio(backtest_scenario: BacktestScenario) -> BacktestResult:
    """Backtest portfolio."""
    # TODO: start_date / end_date is assumed to be month_ends
    not_available = get_invalid_ids([i.id for i in backtest_scenario.portfolio])
    if len(not_available):
        raise HTTPException(
            status_code=404,
            detail=f"Following securities are not available: {not_available}",
        )
    _portfolio_values = run_backtesting(backtest_scenario)
    portfolio_values = [
        PortfolioValue(
            date=row["date"],
            portfolio_value=row["portfolio_value"],
            holdings=[
                Holding(id=id, amount=amount) for id, amount in row.items() if id not in ["date", "portfolio_value"]
            ],
        )
        for row in _portfolio_values.to_dicts()
    ]
    metrics = get_portfolio_metrics(_portfolio_values, backtest_scenario.start_date, backtest_scenario.end_date)
    return BacktestResult(
        metrics=metrics,
        portfolio_values=portfolio_values,
    )
