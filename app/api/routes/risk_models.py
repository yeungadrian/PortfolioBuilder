import numpy as np
import polars as pl
from fastapi import APIRouter

from app.schemas import OptimisationScenario
from app.utils import load_returns

router = APIRouter()


def calculate_sample_covariance(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> np.ndarray:
    """Calculate risk model based on sample covariance."""
    sample_covariance = np.cov(
        df.select(pl.col(ids)).to_numpy(),
        rowvar=False,
    )
    return sample_covariance * frequency


@router.post("/risk-model")
def get_risk_model(scenario: OptimisationScenario) -> list[dict[str, str | float]]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    sample_covariance = calculate_sample_covariance(security_returns, scenario.ids)
    _risk_model = pl.from_numpy(sample_covariance, schema={i: pl.Float64 for i in scenario.ids})

    risk_model: list[dict[str, str | float]] = (
        _risk_model.with_columns(pl.Series(scenario.ids).alias("id")).select(["id", *scenario.ids]).to_dicts()
    )
    return risk_model
