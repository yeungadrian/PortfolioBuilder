import polars as pl
from fastapi import APIRouter, HTTPException

from app.core.config import data_settings
from app.schemas import SecurityDetails

router = APIRouter()


@router.get(
    "/all/",
    summary="Get details for all securities",
    description="Get details for all supported UK securities.",
)
def get_all_details() -> list[SecurityDetails]:
    """Load details for all securities."""
    _all_details = pl.read_parquet(data_settings.security_details).to_dicts()
    all_details = [SecurityDetails(**i) for i in _all_details]
    return all_details


@router.get("/{sedol}/", summary="Get security details by sedol")
def get_details_by_sedol(sedol: str) -> SecurityDetails:
    """Get details for single security by sedol."""
    _security_details = (
        pl.scan_parquet(data_settings.security_details).filter(pl.col("sedol") == sedol).collect().to_dicts()
    )
    if len(_security_details) == 0:
        raise HTTPException(status_code=404, detail=f"sedol: {sedol} does not exist")
    security_details = SecurityDetails(**_security_details[0])
    return security_details
