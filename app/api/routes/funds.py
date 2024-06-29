from typing import Annotated

import polars as pl
from fastapi import APIRouter, Depends

from app.core.config import data_settings
from app.schemas import FundDetails

router = APIRouter()


def load_fund_details() -> list[FundDetails]:
    """
    Load fund details from json.

    Returns
    -------
    list[FundDetails]
        List of available of funds with corresponding details
    """
    _fund_details = pl.read_parquet(data_settings.fund_details)
    fund_details: list[FundDetails] = _fund_details.to_dicts()
    return fund_details


@router.get("/funds/")
def get_available_funds(
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
