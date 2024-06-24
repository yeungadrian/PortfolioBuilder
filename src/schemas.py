from __future__ import annotations

from pydantic import BaseModel, Field


class FundDetails(BaseModel):
    """Fund details."""

    id: str = Field(description="Unique identifier for the fund")
    name: str = Field(description="Name of the fund")
    asset_class: str = Field(
        description="Asset class of the fund (e.g. equity, fixed income, etc.)"
    )
    inception_date: str = Field(description="Date the fund was established")
    benchmark: str = Field(description="Benchmark index for the fund")
    currency_code: str = Field(
        description="Currency code for the fund (e.g. USD, EUR, etc.)"
    )
    sedol: str = Field(
        description="SEDOL (Stock Exchange Daily Official List) code for the fund"
    )
    ocf: str = Field(description="OCF (Ongoing Charges Figure) of the fund")

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
