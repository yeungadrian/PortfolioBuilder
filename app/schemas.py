from pydantic import BaseModel


class FundDetails(BaseModel):
    """Fund details."""

    id: str
    name: str
    asset_class: str
    inception_date: str
    benchmark: str
    currency_code: str
    sedol: str | None
    ocf: str

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
