from fastapi.testclient import TestClient


def test_funds(client: TestClient) -> None:
    response = client.get("/funds/all/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[0]["sedol"] == "B5B71Q7"


def test_funds_sedol_ok(client: TestClient) -> None:
    response = client.get("/funds/B5B71Q7/")
    assert response.status_code == 200
    assert response.json()["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()["currency_code"] == "GBP"


def test_unds_sedol_validation_error(client: TestClient) -> None:
    response = client.get("/funds/FAKESEDOL/")
    assert response.status_code == 404
