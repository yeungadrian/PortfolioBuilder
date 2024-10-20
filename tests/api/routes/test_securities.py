import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_securities() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/securities/all/")
    assert response.status_code == 200
    assert "vanguard-us-equity-index-fund-gbp-acc" in [i["id"] for i in response.json()]


@pytest.mark.anyio
async def test_securities_sedol_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/securities/B5B71Q7/")
    assert response.status_code == 200
    assert response.json()["id"] == "vanguard-us-equity-index-fund-gbp-acc"


@pytest.mark.anyio
async def test_securities_sedol_validation_error() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/securities/FAKEsedol/")
    assert response.status_code == 404
