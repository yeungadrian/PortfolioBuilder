import polars as pl
from fastapi import APIRouter, HTTPException

from app.core.config import data_settings
from app.schemas import BacktestDetail, BacktestScenario

router = APIRouter()


def validate_ids(ids: list[str]) -> None:
    """Validate ids provided."""
    avaliable_ids = (
        pl.scan_parquet(data_settings.fund_details)
        .filter(pl.col("id").is_in(ids))
        .collect()["id"]
        .to_list()
    )

    not_avaliable = [_id for _id in ids if _id not in avaliable_ids]

    if len(not_avaliable) > 0:
        raise HTTPException(
            status_code=404,
            detail=f"Following funds are not avaliable: {not_avaliable}",
        )


@router.post("/")
def backtest_portfolio(backtest_scenario: BacktestScenario) -> list[BacktestDetail]:
    """Backtest portfolio."""
    # TODO: start_date / end_date is assumed to be month_ends
    holdings = {
        holding["id"]: holding["amount"]
        for holding in backtest_scenario.model_dump()["portfolio"]
    }
    ids = list(holdings.keys())

    validate_ids(ids)

    holding_returns = (
        pl.scan_parquet(data_settings.holding_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(
            pl.col("date").is_between(
                backtest_scenario.start_date, backtest_scenario.end_date
            )
        )
        .collect()
    )

    holding_returns = holding_returns.with_columns(
        pl.when(pl.col("date") == pl.col("date").min())
        .then(0)
        .otherwise(pl.col("monthly_return"))
        .alias("monthly_return")
    )

    holding_returns = holding_returns.with_columns(
        pl.col("monthly_return") + 1
    ).with_columns(
        pl.col("monthly_return").cum_prod().over("id").alias("cum_prod") - 1.0
    )

    _backtest_summary = holding_returns.pivot(on="id", values="cum_prod", index="date")
    _backtest_summary = _backtest_summary.with_columns(
        [((pl.col(i) + 1.0) * j).alias(i) for i, j in holdings.items()]
    )
    _backtest_summary = _backtest_summary.with_columns(
        pl.sum_horizontal(ids).alias("portfolio_value")
    )

    backtest_summary = [
        BacktestDetail(
            date=row["date"],
            portfolio_value=row["portfolio_value"],
            holdings=[
                {"id": _id, "amount": amount}
                for _id, amount in row.items()
                if _id not in ["date", "portfolio_value"]
            ],
        )
        for row in _backtest_summary.to_dicts()
    ]

    return backtest_summary
