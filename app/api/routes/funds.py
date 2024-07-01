import polars as pl
from fastapi import APIRouter, HTTPException

from app.core.config import data_settings
from app.schemas import FundDetails

router = APIRouter()


@router.get(
    "/all/",
    summary="Get details for all funds",
    description="Get details for all supported UK funds.",
)
def get_all_details() -> list[FundDetails]:
    """Load details for all funds."""
    _all_details = pl.read_parquet(data_settings.fund_details).to_dicts()
    all_details = [FundDetails(**i) for i in _all_details]
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
    if len(_fund_details) == 0:
        raise HTTPException(status_code=404, detail="Fund not found")
    fund_details = FundDetails(**_fund_details[0])
    return fund_details
