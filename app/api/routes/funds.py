import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

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
    with Path("data/processed/fund_details.json").open(mode="r") as f:
        fund_details: list[FundDetails] = json.load(f)
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
