from typing import Any, Literal

import numpy as np
import polars as pl
from fastapi import APIRouter

from app.data_loader import load_returns
from app.expected_returns import calculate_historical_expected_returns
from app.optimisation import optimise_min_volatility
from app.portfolio_metrics import calculate_portfolio_std
from app.risk_models import calculate_leodit_wolf_covariance, calculate_sample_covariance
from app.schemas import ExpectedReturn, Holding, OptimisationScenario

router = APIRouter()


@router.post("/expected-returns")
def get_expected_returns(scenario: OptimisationScenario) -> list[ExpectedReturn]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids)
    expected_returns: list[ExpectedReturn] = _expected_returns.unpivot(
        value_name="expected_return", variable_name="id"
    ).to_dicts()
    return expected_returns


@router.post("/risk-model")
def get_risk_model(
    scenario: OptimisationScenario, method: Literal["sample_cov", "ledoit_wolf"]
) -> list[dict[str, str | float]]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _security_returns = security_returns.select(pl.col(scenario.ids)).to_numpy()
    match method:
        case "sample_cov":
            covariance = calculate_sample_covariance(_security_returns)
        case "ledoit_wolf":
            covariance = calculate_leodit_wolf_covariance(_security_returns)

    _risk_model = pl.from_numpy(covariance, schema={i: pl.Float64 for i in scenario.ids})

    risk_model: list[dict[str, str | float]] = (
        _risk_model.with_columns(pl.Series(scenario.ids).alias("id")).select(["id", *scenario.ids]).to_dicts()
    )
    return risk_model


@router.post("/mean-variance")
def mean_variance_optimisation(scenario: OptimisationScenario) -> list[Holding]:
    """Run mean variance optimisation."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = calculate_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = calculate_sample_covariance(security_returns.select(pl.col(scenario.ids)).to_numpy())
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    min_vol_portfolio = optimise_min_volatility(expected_returns, sample_covariance, constraints)
    return [Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio, strict=False)]


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
        min_vol_portfolio = optimise_min_volatility(expected_returns, sample_covariance, constraints)
        portfolio_summary = {
            "portfolio": [
                Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio, strict=False)
            ],
            "expected_return": np.sum(expected_returns.T * min_vol_portfolio),
            "implied_standard_deviation": calculate_portfolio_std(min_vol_portfolio, sample_covariance),
        }
        efficient_portfolios.append(portfolio_summary)
    return efficient_portfolios
