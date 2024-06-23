from __future__ import annotations

import polars as pl
from fastapi import APIRouter

router = APIRouter()


@router.get("/funds/")
async def get_funds() -> dict[str, list[str]]:
    """
    Get available funds.

    Returns
    -------
    dict[str,list[str]]
        List of funds

    """
    funds = pl.read_parquet("data/processed/funds.pq")
    funds = funds.get_column("name").to_list()
    result = {"names": funds}
    return result
