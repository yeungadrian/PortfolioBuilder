import pytest
from fastapi.testclient import TestClient


def test_expected_returns(client: TestClient) -> None:
    body = {
        "end_date": "2024-01-01",
        "ids": [
            "vanguard-ftse-100-index-unit-trust-gbp-acc",
            "vanguard-us-equity-index-fund-gbp-acc",
            "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
        ],
        "start_date": "2018-01-01",
    }

    response = client.post("/optimisation/expected-returns/", json=body)
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-ftse-100-index-unit-trust-gbp-acc"
    assert response.json()[0]["expected_return"] == pytest.approx(0.03954420827759142)


def test_risk_model_sample(client: TestClient) -> None:
    body = {
        "end_date": "2024-01-01",
        "ids": [
            "vanguard-ftse-100-index-unit-trust-gbp-acc",
            "vanguard-us-equity-index-fund-gbp-acc",
            "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
        ],
        "start_date": "2018-01-01",
    }

    response = client.post("/optimisation/risk-model?method=sample_cov", json=body)
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-ftse-100-index-unit-trust-gbp-acc"
    assert response.json()[0]["vanguard-ftse-100-index-unit-trust-gbp-acc"] == pytest.approx(0.017994301807337746)


def test_risk_model_leodit(client: TestClient) -> None:
    body = {
        "end_date": "2024-01-01",
        "ids": [
            "vanguard-ftse-100-index-unit-trust-gbp-acc",
            "vanguard-us-equity-index-fund-gbp-acc",
            "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
        ],
        "start_date": "2018-01-01",
    }

    response = client.post("/optimisation/risk-model?method=ledoit_wolf", json=body)
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-ftse-100-index-unit-trust-gbp-acc"

    assert response.json()[0]["vanguard-ftse-100-index-unit-trust-gbp-acc"] == pytest.approx(0.0015309608776905097)
    assert response.json()[0]["vanguard-us-equity-index-fund-gbp-acc"] == pytest.approx(0.0008884771895532375)


def test_min_vol(client: TestClient) -> None:
    body = {
        "end_date": "2024-01-01",
        "ids": [
            "vanguard-ftse-100-index-unit-trust-gbp-acc",
            "vanguard-us-equity-index-fund-gbp-acc",
            "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
        ],
        "start_date": "2018-01-01",
    }

    response = client.post("/optimisation/mean-variance/", json=body)
    assert response.status_code == 200
    assert response.json()[0]["id"] == "vanguard-ftse-100-index-unit-trust-gbp-acc"
    assert response.json()[0]["amount"] == pytest.approx(0.548671633696346)


def test_efficient_frontier(client: TestClient) -> None:
    body = {
        "end_date": "2024-01-01",
        "ids": [
            "vanguard-ftse-100-index-unit-trust-gbp-acc",
            "vanguard-us-equity-index-fund-gbp-acc",
            "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
        ],
        "start_date": "2018-01-01",
    }

    response = client.post("/optimisation/efficient-frontier?n_portfolios=3", json=body)
    assert response.status_code == 200
    assert response.json()[0]["portfolio"][0]["id"] == "vanguard-ftse-100-index-unit-trust-gbp-acc"
    assert response.json()[0]["portfolio"][0]["amount"] == pytest.approx(4.732899320939246e-13)
    assert response.json()[0]["expected_return"] == pytest.approx(-0.05346345590292251)
    assert response.json()[0]["implied_standard_deviation"] == pytest.approx(0.15403819424142662)

    assert response.json()[1]["portfolio"][1]["id"] == "vanguard-us-equity-index-fund-gbp-acc"
    assert response.json()[1]["portfolio"][1]["amount"] == pytest.approx(0.2794289574642864)
    assert response.json()[1]["expected_return"] == pytest.approx(0.03387391520563446)
    assert response.json()[1]["implied_standard_deviation"] == pytest.approx(0.1066544373178886)
