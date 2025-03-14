"""Securities APIRouter."""

import polars as pl
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import SecurityDetails

router = APIRouter()


@router.get(
    "/all/",
    summary="Get details for all securities",
    description="Get details for all supported UK securities.",
)
def get_all_details() -> list[SecurityDetails]:
    """Load details for all securities."""
    _all_details = pl.read_parquet(settings.security_details).to_dicts()
    all_details = [SecurityDetails.model_validate(i) for i in _all_details]
    return all_details


@router.get("/{sedol}/", summary="Get security details by sedol")
def get_details_by_sedol(sedol: str) -> SecurityDetails:
    """Get details for single security by sedol."""
    _security_details = (
        pl.scan_parquet(settings.security_details).filter(pl.col("sedol") == sedol).collect().to_dicts()
    )
    if len(_security_details) == 0:
        raise HTTPException(status_code=404, detail=f"sedol: {sedol} does not exist")
    return SecurityDetails.model_validate(_security_details[0])
