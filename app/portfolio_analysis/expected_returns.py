import polars as pl


def get_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns."""
    inv_years = frequency / df.shape[0]  # equivalent to 1/n
    # Geometric Mean = (1 + r1) *... * (1 + rn)^(1/n) - 1
    expected_returns = (
        df.drop("date")
        .with_columns([(pl.col(id) + 1) for id in ids])
        .product()
        .with_columns([(pl.col(id) ** (inv_years) - 1) for id in ids])
    )
    return expected_returns
