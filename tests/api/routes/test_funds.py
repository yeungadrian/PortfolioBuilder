from fastapi.testclient import TestClient


def test_securities(client: TestClient) -> None:
    response = client.get("/securities/all/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[0]["sedol"] == "B5B71Q7"


def test_securities_sedol_ok(client: TestClient) -> None:
    response = client.get("/securities/B5B71Q7/")
    assert response.status_code == 200
    assert response.json()["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()["currency_code"] == "GBP"


def test_securities_sedol_validation_error(client: TestClient) -> None:
    response = client.get("/securities/FAKESEDOL/")
    assert response.status_code == 404
