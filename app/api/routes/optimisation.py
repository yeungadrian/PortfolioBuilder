from datetime import date
from typing import Any, Callable

import numpy as np
import polars as pl
from fastapi import APIRouter
from scipy.optimize import minimize

from app.core.config import data_settings
from app.schemas import ExpectedReturn, Holding, OptimisationScenario

router = APIRouter()


def load_returns(ids: list[str], start_date: date, end_date: date) -> pl.DataFrame:
    """Load returns for securities."""
    security_returns = (
        pl.scan_parquet(data_settings.fund_returns)
        .filter(pl.col("id").is_in(ids))
        .filter(pl.col("date").is_between(start_date, end_date))
        .collect()
    )
    security_returns = security_returns.pivot(on="id", values="monthly_return", index="date")
    security_returns = security_returns.select(["date", *ids])
    return security_returns


def calculate_historical_expected_returns(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> pl.DataFrame:
    """Calculate historical expected returns."""
    expected_returns = (
        df.with_columns([(pl.col(id) + 1.0) for id in ids])
        .select(ids)
        .product()
        .with_columns([(pl.col(id) ** (frequency / pl.col(id).len()) - 1) for id in ids])
    )
    return expected_returns


def calculate_sample_covariance(df: pl.DataFrame, ids: list[str], frequency: int = 12) -> np.ndarray:
    """Calculate risk model based on sample covariance."""
    sample_covariance = np.cov(
        df.select(pl.col(ids)).to_numpy(),
        rowvar=False,
    )
    return sample_covariance * frequency


@router.post("/expected-returns")
def get_expected_returns(scenario: OptimisationScenario) -> list[ExpectedReturn]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids)
    expected_returns: list[ExpectedReturn] = _expected_returns.melt(
        value_name="expected_return", variable_name="id"
    ).to_dicts()
    return expected_returns


@router.post("/risk-model")
def get_risk_model(scenario: OptimisationScenario) -> list[dict[str, str | float]]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    sample_covariance = calculate_sample_covariance(security_returns, scenario.ids)
    _risk_model = pl.from_numpy(sample_covariance, schema={i: pl.Float64 for i in scenario.ids})

    risk_model: list[dict[str, str | float]] = (
        _risk_model.with_columns(pl.Series(scenario.ids).alias("ids")).select(["ids", *scenario.ids]).to_dicts()
    )
    return risk_model


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
