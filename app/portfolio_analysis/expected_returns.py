"""Module for calculating expected returns."""

import polars as pl


def get_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns.

    Parameters
    ----------
    df : pl.DataFrame
        price history for securities
    ids : list[str]
        securities to calculate expected returns for
    frequency : int, optional
        number of points per year (252 - daily, 12 - monthly, 1 - yearly), by default 12

    Returns
    -------
    pl.DataFrame
        expected return per security
    """
    inv_years = frequency / df.shape[0]  # equivalent to 1/n
    # Geometric Mean = (1 + r1) *... * (1 + rn)^(1/n) - 1
    expected_returns = (
        df.drop("date")
        .with_columns([(pl.col(id) + 1) for id in ids])
        .product()
        .with_columns([(pl.col(id) ** (inv_years) - 1) for id in ids])
    )
    return expected_returns
