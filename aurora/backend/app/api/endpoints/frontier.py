import numpy as np
import pandas as pd
from app import schemas
from app.modules.data_loader import load_historical_returns
from app.modules.frontierCalculator import efficient_frontier_metrics
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def efficient_frontier(item: schemas.frontier):

    fund_codes = item.dict()["funds"]
    start_date = item.dict()["startDate"]
    end_date = item.dict()["endDate"]
    numberOfPortfolios = item.dict()["numberOfPortfolios"]
    frequency = "monthly"

    historical_returns = pd.DataFrame(
        load_historical_returns(
            fund_codes=fund_codes,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )
    )

    fund_returns = np.mean(historical_returns.drop(columns=["date"]))
    fund_covariance = historical_returns.drop(columns=["date"]).cov()

    result = efficient_frontier_metrics(
        fund_returns, fund_covariance, numberOfPortfolios, fund_codes
    )

    return result
