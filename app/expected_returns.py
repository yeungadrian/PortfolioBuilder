import polars as pl


def calculate_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns."""
    years = frequency / df.shape[0]
    expected_returns = (
        df.drop("date")
        .with_columns([(pl.col(id) + 1) for id in ids])
        .product()
        .with_columns([(pl.col(id) ** (years) - 1) for id in ids])
    )
    return expected_returns
