import polars as pl
from fastapi import APIRouter

from app.core.config import data_settings
from app.schemas import BacktestScenario, BacktestSummary

router = APIRouter()


@router.post("/")
def backtest_portfolio(backtest_scenario: BacktestScenario) -> list[BacktestSummary]:
    """Backtest portfolio."""
    # TODO: start_date / end_date is assumed to be month_ends
    holdings = {
        holding["id"]: holding["amount"]
        for holding in backtest_scenario.dict()["portfolio"]
    }
    ids = list(holdings.keys())

    fund_returns = (
        pl.scan_parquet(data_settings.fund_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(
            pl.col("date").is_between(
                backtest_scenario.start_date, backtest_scenario.end_date
            )
        )
        .collect()
    )

    fund_returns = fund_returns.with_columns(
        pl.when(pl.col("date") == pl.col("date").min())
        .then(0)
        .otherwise(pl.col("monthly_return"))
        .alias("monthly_return")
    )

    fund_returns = fund_returns.with_columns(pl.col("monthly_return") + 1).with_columns(
        pl.col("monthly_return").cum_prod().over("id").alias("cum_prod") - 1.0
    )

    summary = fund_returns.pivot(on="id", values="cum_prod", index="date")

    summary = summary.with_columns(
        [((pl.col(i) + 1.0) * j).alias(i) for i, j in holdings.items()]
    )

    summary = summary.with_columns(pl.sum_horizontal(ids).alias("portfolio_value"))

    _backtest_summary = summary.to_dicts()

    backtest_summary = [
        {
            "date": point["date"],
            "portfolio_value": point["portfolio_value"],
            "holdings": [
                {"id": _id, "amount": amount}
                for _id, amount in point.items()
                if _id not in ["date", "portfolio_value"]
            ],
        }
        for point in _backtest_summary
    ]

    return backtest_summary  # type: ignore [return-value]
