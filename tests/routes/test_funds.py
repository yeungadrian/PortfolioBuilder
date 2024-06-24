from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app
from src.routers.funds import load_fund_details


def override_load_fund_details() -> list[dict[str, str]]:
    """
    Load fund details from json.

    Returns
    -------
    list[dict[str,str]]
        List of available of funds with corresponding details
    """
    fund_details = [
        {
            "id": "vanguard-us-equity-index-fund-gbp-acc",
            "name": "U.S. Equity Index Fund",
            "asset_class": "Equity",
            "inception_date": "23 Jun 2009",
            "benchmark": "Standard and Poor&#8217;s Total Market Index",
            "currency_code": "GBP",
            "sedol": "B5B71Q7",
            "ocf": "0.10%",
        }
    ]

    return fund_details


app.dependency_overrides[load_fund_details] = override_load_fund_details


def test_override_in_items(*, client: TestClient) -> None:
    response = client.get("/funds/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[0]["sedol"] == "B5B71Q7"
