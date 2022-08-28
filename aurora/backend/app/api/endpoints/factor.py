import pandas as pd
from app import schemas
from app.modules.data_loader import DataLoader
from app.modules.factor import Factor
from app.modules.factorRegressionCalculator import calculate_factor_regression
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def factor_regression(item: schemas.factor):

    fund_codes = item.dict()["funds"]
    start_date = item.dict()["start_date"]
    end_date = item.dict()["end_date"]
    regression_factors = item.dict()["factors"]
    frequency = item.dict()["frequency"].lower()

    frenchfama_Factors = pd.DataFrame(
        DataLoader().load_ffFactors(
            regression_factors=regression_factors,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )
    )

    historical_returns = pd.DataFrame(
        DataLoader().load_historical_returns(
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


"""
@router.post("/v2/")
def regress_funds(item: schemas.factor):

    fund_codes = item.dict()["funds"]
    start_date = item.dict()["start_date"]
    end_date = item.dict()["end_date"]
    regression_factors = item.dict()["factors"]
    frequency = item.dict()["frequency"].lower()

    ff_factors = DataLoader().load_ff_factors(
        regression_factors=regression_factors,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )

    historical_returns = pd.DataFrame(
        load_historical_returns(
            fund_codes=fund_codes,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )
    )

    external_data = {
        "fund_codes": fund_codes,
        "start_date": start_date,
        "end_date": end_date,
        "price_df": historical_returns,
        "french_fama_df": ff_factors,
    }

    Factor(**external_data)

    output = []

    for i in fund_codes:

        result = calculate_factor_regression(
            fund_code=i,
            regression_factors=regression_factors,
            historical_returns=historical_returns,
            frenchfama_Factors=ff_factors,
        )
        output.append(result)

    return output
    """
