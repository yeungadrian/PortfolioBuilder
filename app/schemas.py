from datetime import date

from pydantic import BaseModel


class FundDetails(BaseModel):
    """Fund details."""

    id: str
    name: str
    asset_class: str
    inception_date: date
    benchmark: str | None
    currency_code: str
    sedol: str | None
    ocf: str | None
    returns_ytd: float | None
    returns_1yr: float | None
    returns_3yr: float | None
    returns_5yr: float | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "vanguard-us-equity-index-fund-gbp-acc",
                    "name": "U.S. Equity Index Fund",
                    "asset_class": "Equity",
                    "inception_date": "23 Jun 2009",
                    "benchmark": "Standard and Poor&#8217;s Total Market Index",
                    "currency_code": "GBP",
                    "sedol": "B5B71Q7",
                    "ocf": "0.10%",
                }
            ]
        }
    }


class Holding(BaseModel):
    """Fund holding."""

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


class BacktestDetail(BaseModel):
    """Backtest details per date."""

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
