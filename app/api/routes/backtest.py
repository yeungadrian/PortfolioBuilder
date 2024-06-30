from datetime import date

import polars as pl
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import data_settings

router = APIRouter()


class Holding(BaseModel):
    """Fund holding."""

    id: str
    amount: float


class BacktestScenario(BaseModel):
    """Backtest Settings."""

    portfolio: list[Holding]
    start_date: date
    end_date: date

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "portfolio": [
                        {
                            "id": "vanguard-us-equity-index-fund-gbp-acc",
                            "amount": 1000.0,
                        }
                    ],
                    "start_date": date(2020, 1, 1),
                    "end_date": date(2024, 1, 1),
                }
            ]
        }
    }


@router.post("/")
def backtest_portfolio(config: BacktestScenario) -> dict[str, str]:
    """Backtest portfolio."""
    pl.scan_parquet(data_settings.fund_returns)
    return {"status": "ok"}
