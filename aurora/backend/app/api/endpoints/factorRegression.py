from fastapi import APIRouter

from app import schemas
from app.modules.dataLoader import load_historical_returns, load_ffFactors
from app.modules.factorRegressionCalculator import calculate_factor_regression
import pandas as pd

router = APIRouter()


@router.post("/")
def factor_regression(item: schemas.factorRegression):

    fund_codes = item.dict()["funds"]
    start_date = item.dict()["startDate"]
    end_date = item.dict()["endDate"]
    regression_factors = item.dict()["regressionFactors"]
    frequency = item.dict()["frequency"].lower()

    frenchfama_Factors = pd.DataFrame(
        load_ffFactors(
            regression_factors=regression_factors,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )
    )

    historical_returns = pd.DataFrame(
        load_historical_returns(
            fund_codes=fund_codes,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )
    )

    output = []

    for i in fund_codes:

        result = calculate_factor_regression(
            fund_code=i,
            regression_factors=regression_factors,
            historical_returns=historical_returns,
            frenchfama_Factors=frenchfama_Factors,
        )
        output.append(result)

    return output
