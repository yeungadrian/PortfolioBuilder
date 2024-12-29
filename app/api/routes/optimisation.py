from typing import Literal

import numpy as np
import polars as pl
from fastapi import APIRouter

from app.loader import load_returns
from app.models import (
    EfficientFrontierPortfolio,
    ExpectedReturn,
    Holding,
    OptimisationScenario,
)
from app.portfolio_analysis.expected_returns import get_historical_expected_returns
from app.portfolio_analysis.metrics import get_portfolio_std
from app.portfolio_analysis.optimisation import get_min_vol_portfolio
from app.portfolio_analysis.risk_models import (
    get_leodit_wolf_covariance,
    get_sample_covariance,
)

router = APIRouter()


@router.post("/expected-returns")
def get_expected_returns(scenario: OptimisationScenario) -> list[ExpectedReturn]:
    """Get expected returns based on historical returns."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    _expected_returns = get_historical_expected_returns(security_returns, scenario.ids)
    expected_returns = _expected_returns.unpivot(
        value_name="expected_return", variable_name="id"
    ).to_dicts()
    expected_returns = [ExpectedReturn.model_validate(i) for i in expected_returns]
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
            covariance = get_sample_covariance(_security_returns)
        case "ledoit_wolf":
            covariance = get_leodit_wolf_covariance(_security_returns)

    _risk_model = pl.from_numpy(covariance, schema={i: pl.Float64 for i in scenario.ids})

    risk_model: list[dict[str, str | float]] = (
        _risk_model.with_columns(pl.Series(scenario.ids).alias("id"))
        .select(["id", *scenario.ids])
        .to_dicts()
    )
    return risk_model


@router.post("/mean-variance")
def mean_variance_optimisation(scenario: OptimisationScenario) -> list[Holding]:
    """Run mean variance optimisation."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = get_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = get_sample_covariance(security_returns.select(pl.col(scenario.ids)).to_numpy())
    constraints = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
    min_vol_portfolio = get_min_vol_portfolio(expected_returns, sample_covariance, constraints)
    return [
        Holding(id=id, amount=ratio) for id, ratio in zip(scenario.ids, min_vol_portfolio, strict=False)
    ]


@router.post("/efficient-frontier")
def efficient_frontier(
    scenario: OptimisationScenario, n_portfolios: int = 5
) -> list[EfficientFrontierPortfolio]:
    """Generate efficient frontier portfolios."""
    security_returns = load_returns(scenario.ids, scenario.start_date, scenario.end_date)
    expected_returns = get_historical_expected_returns(security_returns, scenario.ids).to_numpy().T
    sample_covariance = get_sample_covariance(security_returns.select(pl.col(scenario.ids)).to_numpy())
    efficient_portfolios = []
    for target_return in np.linspace(min(expected_returns), max(expected_returns), n_portfolios):
        constraints = (
            {
                "type": "eq",
                "fun": lambda x: np.sum(expected_returns.T * x) - target_return,  # noqa: B023
            },
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
        )
        min_vol_portfolio = get_min_vol_portfolio(expected_returns, sample_covariance, constraints)
        efficient_portfolios.append(
            EfficientFrontierPortfolio(
                portfolio=[
                    Holding(id=id, amount=ratio)
                    for id, ratio in zip(scenario.ids, min_vol_portfolio, strict=False)
                ],
                expected_return=np.sum(expected_returns.T * np.array(min_vol_portfolio)),
                implied_standard_deviation=get_portfolio_std(
                    np.array(min_vol_portfolio), sample_covariance
                ),
            )
        )
    return efficient_portfolios
