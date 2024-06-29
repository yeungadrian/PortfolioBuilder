from fastapi.testclient import TestClient

from app.api.routes.funds import load_details
from app.main import app


def override_load_details() -> list[dict[str, str]]:
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


app.dependency_overrides[load_details] = override_load_details


def test_funds_ok(*, client: TestClient) -> None:
    response = client.get("/funds/all/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[0]["sedol"] == "B5B71Q7"
