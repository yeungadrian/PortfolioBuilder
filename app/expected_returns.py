"""
Expected returns related endpoints.

This module provides:
- router: router with relevant expected returns endpoints
"""

import polars as pl


def calculate_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns."""
    count = df.shape[0]
    expected_returns = (
        df.with_columns([(pl.col(id) + 1.0) for id in ids])
        .select(ids)
        .product()
        .with_columns([(pl.col(id) ** (frequency / count) - 1) for id in ids])
    )
    return expected_returns
