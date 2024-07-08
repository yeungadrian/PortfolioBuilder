import numpy as np
import polars as pl
from fastapi import APIRouter
from scipy.optimize import minimize

from app.core.config import data_settings
from app.schemas import OptimisationScenario

router = APIRouter()


def calculate_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns."""
    expected_returns = (
        df.with_columns([(pl.col(id) + 1.0) for id in ids])
        .select(ids)
        .product()
        .with_columns([(pl.col(id) ** (frequency / pl.col(id).len()) - 1) for id in ids])
    )
    return expected_returns


def portfolio_std(weights: np.ndarray, fund_covariance: np.ndarray) -> float:
    """Calculate portfolio standard deviation using covariance."""
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(fund_covariance, weights)))
    return float(std)


def optimise_std(
    expected_returns: np.ndarray,
    risk_model: np.ndarray,
) -> list[float]:
    """Use optimisation to find portfolio with minimum std for a given return."""
    args = risk_model
    num_funds = len(expected_returns)

    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    bounds = tuple((0, 1) for i in range(num_funds))
    initial_weights = num_funds * [
        1.0 / num_funds,
    ]
    _result = minimize(
        portfolio_std,
        initial_weights,
        args=args,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    ).x
    result = [float(round(elem)) for elem in _result]
    return result


@router.post("/mean-variance")
def mean_variance_optimisation(scenario: OptimisationScenario) -> str:
    """Run mean variance optimisation."""
    holding_returns = (
        pl.scan_parquet(data_settings.fund_returns)
        .filter(pl.col("id").is_in(scenario.ids))
        .filter(pl.col("date").is_between(scenario.start_date, scenario.end_date))
        .collect()
    )

    holding_returns = holding_returns.pivot(on="id", values="monthly_return", index="date")
    expected_returns = calculate_historical_expected_returns(holding_returns, scenario.ids).to_numpy().T

    sample_covariance = np.cov(
        holding_returns.select(pl.col(scenario.ids)).to_numpy(),
        rowvar=False,
    )

    print(optimise_std(expected_returns, sample_covariance))

    return "WIP"
