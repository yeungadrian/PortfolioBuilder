import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_securities(async_client: AsyncClient) -> None:
    response = await async_client.get("/securities/all/")
    assert response.status_code == 200
    assert "vanguard-us-equity-index-fund-gbp-acc" in [i["id"] for i in response.json()]


@pytest.mark.anyio
async def test_securities_sedol_ok(async_client: AsyncClient) -> None:
    response = await async_client.get("/securities/B5B71Q7/")
    assert response.status_code == 200
    assert response.json()["id"] == "vanguard-us-equity-index-fund-gbp-acc"


@pytest.mark.anyio
async def test_securities_sedol_validation_error(async_client: AsyncClient) -> None:
    response = await async_client.get("/securities/FAKEsedol/")
    assert response.status_code == 404
