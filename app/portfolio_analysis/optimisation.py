"""Module to run optimisation."""

from collections.abc import Callable
from typing import Any

import numpy as np
from scipy.optimize import minimize

from app.portfolio_analysis.metrics import get_portfolio_std


def optimise(
    func: Callable[..., float],
    args: np.ndarray,
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


def get_min_vol_portfolio(
    expected_returns: np.ndarray, risk_model: np.ndarray, constraints: tuple[Any, ...]
) -> list[float]:
    """Use optimisation to find portfolio with minimum std for a given return."""
    n_securities = expected_returns.shape[0]
    initial_weights = np.repeat(1.0 / n_securities, n_securities)
    bounds = tuple((0.0, 1.0) for i in np.nditer(expected_returns))
    _result = optimise(get_portfolio_std, risk_model, bounds, constraints, initial_weights)
    return _result
