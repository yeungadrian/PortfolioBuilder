"""Pydantic based schemas for data validation."""

from datetime import date

from pydantic import BaseModel


class SecurityDetails(BaseModel):
    """Security details."""

    id: str
    name: str
    asset_class: str
    inception_date: date
    sedol: str
    ocf: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "vanguard-us-equity-index-fund-gbp-acc",
                    "name": "U.S. Equity Index Fund",
                    "asset_class": "Equity",
                    "inception_date": "2009-06-23",
                    "sedol": "B5B71Q7",
                    "ocf": "0.10%",
                }
            ]
        }
    }


class Holding(BaseModel):
    """Security holding."""

    id: str
    amount: float


class BacktestScenario(BaseModel):
    """Backtest Settings."""

    portfolio: list[Holding]
    start_date: date
    end_date: date

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "portfolio": [
                        {
                            "id": "vanguard-us-equity-index-fund-gbp-acc",
                            "amount": 100.0,
                        },
                        {
                            "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
                            "amount": 100.0,
                        },
                    ],
                    "start_date": date(2023, 1, 1),
                    "end_date": date(2024, 1, 1),
                }
            ]
        }
    }


class PortfolioValue(BaseModel):
    """Portfolio value with breakdown per holding."""

    date: date
    portfolio_value: float
    holdings: list[Holding]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-01-01",
                    "portfolio": 200.0,
                    "holdings": [
                        {
                            "id": "vanguard-us-equity-index-fund-gbp-acc",
                            "amount": 100.0,
                        },
                        {
                            "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
                            "amount": 100.0,
                        },
                    ],
                }
            ]
        }
    }


class PortfolioMetrics(BaseModel):
    """Common portfolio metrics."""

    portfolio_return: float
    cagr: float
    standard_deviation: float
    max_drawdown: float


class BacktestResult(BaseModel):
    """Backtest result."""

    metrics: PortfolioMetrics
    portfolio_values: list[PortfolioValue]


class OptimisationScenario(BaseModel):
    """Optimisation settings."""

    start_date: date
    end_date: date
    ids: list[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start_date": date(2018, 1, 1),
                    "end_date": date(2024, 1, 1),
                    "ids": [
                        "vanguard-ftse-100-index-unit-trust-gbp-acc",
                        "vanguard-us-equity-index-fund-gbp-acc",
                        "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
                    ],
                }
            ]
        }
    }


class ExpectedReturn(BaseModel):
    """Expected return for a security."""

    id: str
    expected_return: float

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": "vanguard-us-equity-index-fund-gbp-acc", "expected_returns": 6.752961}]
        }
    }


class EfficientFrontierPortfolio(BaseModel):
    """Efficient frontier portfolios."""

    portfolio: list[Holding]
    expected_return: float
    implied_standard_deviation: float
