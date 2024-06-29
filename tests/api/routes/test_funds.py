from fastapi.testclient import TestClient


def test_funds_ok(*, client: TestClient) -> None:
    response = client.get("/funds/all/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[0]["sedol"] == "B5B71Q7"
