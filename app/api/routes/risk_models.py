from typing import Literal

import numpy as np
import polars as pl
from fastapi import APIRouter
from sklearn.covariance import ledoit_wolf

from app.schemas import OptimisationScenario
from app.utils import load_returns

router = APIRouter()


def calculate_sample_covariance(security_returns: np.ndarray, frequency: int = 12) -> np.ndarray:
    """Calculate risk model based on sample covariance."""
    sample_covariance = np.cov(
        security_returns,
        rowvar=False,
    )
    return sample_covariance * frequency


def leodit_wolf_covariance(security_returns: np.ndarray) -> np.ndarray:
    """_Calculate Ledoit-Wolf shrinkage estimate for a particular shrinkage target."""
    shrunk_cov, _ = ledoit_wolf(security_returns)
    return shrunk_cov


@router.post("/risk-model")
def get_risk_model(
    scenario: OptimisationScenario, method: Literal["sample_cov", "ledoit_wolf"]
) -> list[dict[str, str | float]]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _security_returns = security_returns.select(pl.col(scenario.ids)).to_numpy()
    match method:
        case "sample_cov":
            sample_covariance = calculate_sample_covariance(_security_returns)
        case "ledoit_wolf":
            sample_covariance = leodit_wolf_covariance(_security_returns)

    _risk_model = pl.from_numpy(sample_covariance, schema={i: pl.Float64 for i in scenario.ids})

    risk_model: list[dict[str, str | float]] = (
        _risk_model.with_columns(pl.Series(scenario.ids).alias("id")).select(["id", *scenario.ids]).to_dicts()
    )
    return risk_model
