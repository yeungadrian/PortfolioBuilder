from fastapi import APIRouter

from app import schemas
from app.modules.dataLoader import load_normalised_historical_index
from app.modules.backtestCalculator import backtest_strategy
from app.modules.metricCalculator import calculate_metrics

router = APIRouter()


@router.post("/")
def backtest_portfolio(item: schemas.backtest):
    portfolio = item.dict()["portfolio"]
    fund_codes = []
    for i in portfolio:
        fund_codes.append(i["fund"])
    historicalData = load_normalised_historical_index(
        fund_codes=fund_codes,
        start_date=item.dict()["startDate"],
        end_date=item.dict()["endDate"],
    )
    backtest_result = backtest_strategy(
        historical_index=historicalData,
        portfolio=portfolio,
        strategy=item.dict()["strategy"],
        start_date=item.dict()["startDate"],
        end_date=item.dict()["endDate"],
    )
    backtest_metrics = calculate_metrics(backtest_result)
    result = {"projection": backtest_result, "metrics": backtest_metrics}
    return result
