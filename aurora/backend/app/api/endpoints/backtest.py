import json

from app import schemas
from app.modules.backtestCalculator import backtest_strategy
from app.modules.dataLoader import DataLoader, load_normalised_historical_index
from app.modules.metricCalculator import calculate_metrics
from app.modules.metrics import Metrics
from app.modules.portfolio import Portfolio
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def backtest_portfolio(item: schemas.portfolio):
    portfolio = item.dict()["portfolio"]
    fund_codes = []
    fund_amount = []

    for i in portfolio:
        fund_codes.append(i["fund"])
        fund_amount.append(i["amount"])

    historical_data = DataLoader().load_historical_index(
        fund_codes,
        item.dict()["start_date"],
        item.dict()["end_date"],
    )

    projection = Portfolio(
        codes=fund_codes,
        amounts=fund_amount,
        start_date=item.dict()["start_date"],
        end_date=item.dict()["end_date"],
        timeseries=historical_data,
        rebalance=item.dict()["strategy"]["rebalance"],
        rebalance_frequency=item.dict()["strategy"]["rebalance_frequency"],
    ).backtest_strategy()

    sp500 = DataLoader().load_sp500(item.dict()["start_date"], item.dict()["end_date"])

    projection = projection.merge(sp500[["date", "market"]], how="left", on="date")

    metrics = Metrics().metrics(projection)

    projection["date"] = projection["date"].dt.strftime("%Y-%m-%d")

    result = {}
    result["metrics"] = metrics
    result["projection"] = json.loads(projection.to_json(orient="records"))

    return result
