from fastapi.testclient import TestClient


def test_securities(client: TestClient) -> None:
    response = client.get("/securities/all/")
    assert response.status_code == 200
    assert "vanguard-us-equity-index-fund-gbp-acc" in [i["id"] for i in response.json()]


def test_securities_sedol_ok(client: TestClient) -> None:
    response = client.get("/securities/B5B71Q7/")
    assert response.status_code == 200
    assert response.json()["id"] == "vanguard-us-equity-index-fund-gbp-acc"


def test_securities_sedol_validation_error(client: TestClient) -> None:
    response = client.get("/securities/FAKEsedol/")
    assert response.status_code == 404
