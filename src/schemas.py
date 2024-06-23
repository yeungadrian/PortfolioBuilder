from __future__ import annotations

from pydantic import BaseModel


class FundDescription(BaseModel):
    """Single asset allocation."""

    fund: str
    value: float
