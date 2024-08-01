from datetime import date

import polars as pl
from fastapi import APIRouter, HTTPException, Request

from app.core.config import data_settings
from app.schemas import BacktestDetails, BacktestProjection, BacktestScenario, PortfolioMetrics
from app.utils import load_returns

router = APIRouter()


def month_diff(date1: date, date2: date) -> int:
    """Calculate difference of two dates in months."""
    diff_in_months = (date2.year - date1.year) * 12 + (date2.month - date1.month)
    return diff_in_months


def invalid_ids(ids: list[str]) -> list[str]:
    """Validate ids provided."""
    avaliable_ids = (
        pl.scan_parquet(data_settings.fund_details).filter(pl.col("id").is_in(ids)).collect()["id"].to_list()
    )
    not_avaliable = [_id for _id in ids if _id not in avaliable_ids]
    return not_avaliable


@router.post("/")
def backtest_portfolio(request: Request, backtest_scenario: BacktestScenario) -> BacktestDetails:
    """Backtest portfolio."""
    # TODO: start_date / end_date is assumed to be month_ends
    holdings = {holding["id"]: holding["amount"] for holding in backtest_scenario.model_dump()["portfolio"]}
    ids = list(holdings.keys())

    not_avaliable = invalid_ids(ids)
    if len(not_avaliable):
        request.state.logger.warning(f"Following funds are not avaliable: {not_avaliable}")
        raise HTTPException(
            status_code=404,
            detail=f"Following funds are not avaliable: {not_avaliable}",
        )

    security_returns = load_returns(ids, backtest_scenario.start_date, backtest_scenario.end_date)

    security_returns = security_returns.with_columns(
        [pl.when(pl.col("date") == pl.col("date").min()).then(0).otherwise(pl.col(_id)).alias(_id) for _id in ids]
    )

    security_returns = security_returns.with_columns([(pl.col(_id) + 1.0).cum_prod().alias(_id) - 1.0 for _id in ids])
    security_returns = security_returns.with_columns([((pl.col(i) + 1.0) * j).alias(i) for i, j in holdings.items()])
    security_returns = security_returns.with_columns(pl.sum_horizontal(ids).alias("portfolio_value"))

    backtest_projection = [
        BacktestProjection(
            date=row["date"],
            portfolio_value=row["portfolio_value"],
            holdings=[
                {"id": _id, "amount": amount} for _id, amount in row.items() if _id not in ["date", "portfolio_value"]
            ],
        )
        for row in security_returns.to_dicts()
    ]

    security_returns = security_returns.with_columns(
        (pl.col("portfolio_value") / pl.col("portfolio_value").shift() - 1).alias("portfolio_return")
    )

    start_value = security_returns["portfolio_value"].head(1)[0]
    end_value = security_returns["portfolio_value"].tail(1)[0]
    n_years = month_diff(backtest_scenario.start_date, backtest_scenario.end_date) / 12

    metrics = {
        "portfolio_return": (end_value / start_value) - 1,
        "cagr": ((end_value / start_value) ** (1 / n_years)) - 1,
        "variance": security_returns["portfolio_return"].var(),
    }

    return BacktestDetails(
        metrics=PortfolioMetrics.model_validate(metrics),
        projection=backtest_projection,
    )
