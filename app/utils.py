from datetime import date

import polars as pl

from app.core.config import data_settings


def load_returns(ids: list[str], start_date: date, end_date: date) -> pl.DataFrame:
    """Load returns for securities."""
    security_returns = (
        pl.scan_parquet(data_settings.fund_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(pl.col("date").is_between(start_date, end_date))
        .collect()
    )
    security_returns = security_returns.pivot(on="id", values="monthly_return", index="date")
    security_returns = security_returns.select(["date", *ids])
    return security_returns
