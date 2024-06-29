from typing import Annotated, Any

import polars as pl
from fastapi import APIRouter, Depends

from app.core.config import data_settings
from app.schemas import FundDetails

router = APIRouter()


def load_fund_details() -> Any:
    """
    Load fund details from json.

    Returns
    -------
    list[dict[str, Any]]
        List of available of funds with corresponding details
    """
    _fund_details = pl.read_parquet(data_settings.fund_details)
    fund_details = _fund_details.to_dicts()
    return fund_details


@router.get("/all/")
def get_fund_details(
    fund_details: Annotated[list[FundDetails], Depends(load_fund_details)],
) -> list[FundDetails]:
    """
    Get available funds with details.

    Returns
    -------
    list[FundDetails]
        List of available of funds with corresponding details
    """
    return fund_details


@router.get("/ids/")
def get_all_fund_details() -> Any:
    """Get available fund ids with display name."""
    lf = pl.scan_parquet(data_settings.fund_details).select(pl.col(["id", "name"]))
    lfc = lf.collect()
    ids = lfc.to_dicts()
    return ids
