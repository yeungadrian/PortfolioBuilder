import polars as pl
from fastapi import APIRouter

from app.schemas import ExpectedReturn, OptimisationScenario
from app.utils import load_returns

router = APIRouter()


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


@router.post("/expected-returns")
def get_expected_returns(scenario: OptimisationScenario) -> list[ExpectedReturn]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids)
    expected_returns: list[ExpectedReturn] = _expected_returns.unpivot(
        value_name="expected_return", variable_name="id"
    ).to_dicts()
    return expected_returns
