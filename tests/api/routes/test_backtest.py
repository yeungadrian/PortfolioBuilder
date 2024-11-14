import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_backtest(async_client: AsyncClient) -> None:
    """Backtest with two valid securities."""
    body = {
        "start_date": "2023-11-30",
        "end_date": "2024-01-31",
        "portfolio": [
            {"amount": 100, "id": "vanguard-us-equity-index-fund-gbp-acc"},
            {
                "amount": 100,
                "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
            },
        ],
    }
    response = await async_client.post("/backtest", json=body)
    assert response.status_code == 200
    assert response.json()["portfolio_values"][0]["portfolio_value"] == pytest.approx(200.0)
    assert response.json()["portfolio_values"][1]["date"] == "2023-12-31"
    assert response.json()["portfolio_values"][1]["portfolio_value"] == pytest.approx(211.5677910878)
    assert response.json()["portfolio_values"][2]["portfolio_value"] == pytest.approx(207.67257285005837)


@pytest.mark.anyio
async def test_backtest_validation_error(async_client: AsyncClient) -> None:
    """Backtest with invalid security."""
    body = {
        "start_date": "2023-11-30",
        "end_date": "2024-01-31",
        "portfolio": [
            {"amount": 100, "id": "fake_fund"},
            {
                "amount": 100,
                "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
            },
        ],
    }
    response = await async_client.post("/backtest", json=body)
    assert response.status_code == 404
