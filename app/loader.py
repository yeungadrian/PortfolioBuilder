from datetime import date

import polars as pl

from app.core.config import settings


def load_returns(ids: list[str], start_date: date, end_date: date) -> pl.DataFrame:
    """Load returns for securities."""
    security_returns = (
        pl.scan_parquet(settings.security_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(pl.col("date").is_between(start_date, end_date))
        .collect()
    )
    # Pivot table so each security becomes a single column
    security_returns = security_returns.pivot(on="id", values="monthly_return", index="date")
    return security_returns
