from collections.abc import Callable
from typing import Any

import numpy as np
from scipy.optimize import minimize


def calculate_portfolio_std(weights: np.ndarray, fund_covariance: np.ndarray) -> float:
    """Calculate portfolio standard deviation using covariance."""
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(fund_covariance, weights)))
    return float(std)


def optimise(
    func: Callable[..., float],
    args: tuple[np.ndarray],
    bounds: tuple[tuple[float, float], ...],
    constraints: tuple[Any, ...],
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


def min_volatility(expected_returns: np.ndarray, risk_model: np.ndarray, constraints: tuple[Any, ...]) -> list[float]:
    """Use optimisation to find portfolio with minimum std for a given return."""
    n_securities = expected_returns.shape[0]
    args = risk_model
    initial_weights = np.repeat(1.0 / n_securities, n_securities)
    bounds = tuple((0.0, 1.0) for i in np.nditer(expected_returns))
    _result = optimise(calculate_portfolio_std, args, bounds, constraints, initial_weights)
    return _result
