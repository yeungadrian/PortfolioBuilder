from __future__ import annotations

from pydantic import BaseModel


class Allocation(BaseModel):
    """Single asset allocation."""

    fund: str
    value: float


class Porfolio(BaseModel):
    """Asset portfolio schema."""

    start_date: str
    end_date: str
    allocation: list[Allocation]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start_date": "2020-01-01",
                    "end_date": "2022-12-31",
                    "allocation": [
                        {
                            "fund": "Vanguard FTSE Dev €pe ex-UK Eq Idx £ Acc",
                            "value": 100.0,
                        },
                        {
                            "fund": "Vanguard Jpn Govt Bd Idx £ H Acc",
                            "value": 100.0,
                        },
                    ],
                }
            ]
        }
    }
