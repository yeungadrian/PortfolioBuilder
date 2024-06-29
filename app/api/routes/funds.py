from typing import Annotated

import polars as pl
from fastapi import APIRouter, Depends

from app.core.config import data_settings
from app.schemas import FundDetails

router = APIRouter()


def load_details() -> list[FundDetails]:
    """
    Load fund details from json.

    Returns
    -------
    list[FundDetails]
        List of available of funds with corresponding details
    """
    _all_details = pl.read_parquet(data_settings.fund_details).to_dicts()
    all_details = [FundDetails.model_validate(i) for i in _all_details]
    return all_details


@router.get("/all/", summary="Get all funds details")
def get_all_details(
    all_details: Annotated[list[FundDetails], Depends(load_details)],
) -> list[FundDetails]:
    """
    Get available funds with details.

    Returns
    -------
    list[FundDetails]
        List of available of funds with corresponding details
    """
    return all_details


@router.get("/{sedol}/", summary="Get fund details by sedol")
def get_details_by_sedol(sedol: str) -> FundDetails:
    """Get details for single fund by sedol."""
    _fund_details = (
        pl.scan_parquet(data_settings.fund_details)
        .filter(pl.col("sedol") == sedol)
        .collect()
        .to_dicts()
    )
    fund_details = FundDetails(**_fund_details[0])
    return fund_details
