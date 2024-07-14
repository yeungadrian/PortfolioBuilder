from typing import Any, Callable

import numpy as np
from fastapi import APIRouter
from scipy.optimize import minimize

from app.api.routes.expected_returns import calculate_historical_expected_returns
from app.api.routes.risk_models import calculate_sample_covariance
from app.api.routes.utils import load_returns
from app.schemas import Holding, OptimisationScenario

router = APIRouter()


def calculate_portfolio_std(weights: np.ndarray, fund_covariance: np.ndarray) -> float:
    """Calculate portfolio standard deviation using covariance."""
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(fund_covariance, weights)))
    return float(std)


def optimise(
    func: Callable[..., float],
    args: tuple[np.ndarray],
    bounds: tuple[tuple[float, float], ...],
    constraints: tuple[dict[str, Any]],
    initial_weights: np.ndarray,
) -> list[float]:
    """Scipy minimize."""
    _result: list[float] = minimize(
        func,
        initial_weights,
        args=args,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    ).x.tolist()

    return _result


def min_volatility(
    expected_returns: np.ndarray,
    risk_model: np.ndarray,
) -> list[float]:
    """Use optimisation to find portfolio with minimum std for a given return."""
    n_securities = expected_returns.shape[0]
    args = risk_model
    initial_weights = np.repeat(1.0 / n_securities, n_securities)
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    bounds = tuple((0.0, 1.0) for i in np.nditer(expected_returns))
    _result = optimise(calculate_portfolio_std, args, bounds, constraints, initial_weights)
    return _result


@router.post("/mean-variance")
def mean_variance_optimisation(scenario: OptimisationScenario) -> list[Holding]:
    """Run mean variance optimisation."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = calculate_sample_covariance(security_returns, scenario.ids)
    min_vol_portfolio = min_volatility(expected_returns, sample_covariance)
    return [Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio)]
