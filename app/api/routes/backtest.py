from typing import Any

import polars as pl
from fastapi import APIRouter

from app.core.config import data_settings
from app.schemas import BacktestScenario

router = APIRouter()


@router.post("/")
def backtest_portfolio(backtest_scenario: BacktestScenario) -> Any:
    """Backtest portfolio."""
    ids = [holding["id"] for holding in backtest_scenario.dict()["portfolio"]]
    _df = (
        pl.scan_parquet(data_settings.fund_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(
            pl.col("date").is_between(
                backtest_scenario.start_date, backtest_scenario.end_date
            )
        )
        .collect()
    )
    _df = _df.with_columns(pl.col("monthly_return") + 1).with_columns(
        pl.col("monthly_return").cum_prod().over("id").alias("cum_prod") - 1.0
    )
    return _df.to_dicts()
