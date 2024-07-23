from typing import Any, Callable

import numpy as np
import polars as pl
from fastapi import APIRouter
from scipy.optimize import minimize

from app.api.routes.expected_returns import calculate_historical_expected_returns
from app.api.routes.risk_models import calculate_sample_covariance
from app.schemas import Holding, OptimisationScenario
from app.utils import load_returns

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


@router.post("/mean-variance")
def mean_variance_optimisation(scenario: OptimisationScenario) -> list[Holding]:
    """Run mean variance optimisation."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = calculate_sample_covariance(security_returns.select(pl.col(scenario.ids)).to_numpy())
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    min_vol_portfolio = min_volatility(expected_returns, sample_covariance, constraints)
    return [Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio)]


@router.post("/efficient-frontier")
def efficient_frontier(scenario: OptimisationScenario, n_portfolios: int = 5) -> Any:
    """Generate efficient frontier portfolios."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = calculate_sample_covariance(security_returns.select(pl.col(scenario.ids)).to_numpy())
    efficient_portfolios = []
    for target_return in np.linspace(min(expected_returns), max(expected_returns), n_portfolios):
        constraints = (
            {"type": "eq", "fun": lambda x: np.sum(expected_returns.T * x) - target_return},  # noqa: B023
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
        )
        min_vol_portfolio = min_volatility(expected_returns, sample_covariance, constraints)
        portfolio_summary = {
            "portfolio": [Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio)],
            "expected_return": np.sum(expected_returns.T * min_vol_portfolio),
            "variance": calculate_portfolio_std(min_vol_portfolio, sample_covariance),
        }
        efficient_portfolios.append(portfolio_summary)
    return efficient_portfolios
