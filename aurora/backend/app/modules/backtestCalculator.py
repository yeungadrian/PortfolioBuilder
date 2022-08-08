import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

from app.modules.metricCalculator import calculate_historical_max


def backtest_funds(
    fund_amount,
    fund_codes,
    fund_index,
):
    number_funds = len(fund_codes)

    fund_diagonal = np.zeros((number_funds, number_funds))
    np.fill_diagonal(fund_diagonal, fund_amount)

    result = fund_index[fund_codes].dot(fund_diagonal)
    result.columns = fund_codes

    result["portfolio"] = result.sum(axis=1)

    return result


def backtest_strategy(historical_index, portfolio, strategy, start_date, end_date):
    fund_index = pd.DataFrame(historical_index)
    fund_codes = []
    fund_amount = []

    for i in portfolio:
        fund_codes.append(i["fund"])
        fund_amount.append(i["amount"])

    dates = fund_index["date"]

    if strategy["rebalance"]:
        fund_percentage = [i / sum(fund_amount) for i in fund_amount]

        frequency = {"y": 12, "q": 3, "m": 1}

        rebalance_frequency = frequency[strategy["rebalanceFrequency"].lower()]

        fund_index["date"] = pd.to_datetime(fund_index["date"])

        month_end_dates = fund_index[fund_index["date"].dt.is_month_end][
            "date"
        ].reset_index(drop=True)
        rebalancing_dates = month_end_dates[
            month_end_dates.index % rebalance_frequency == 0
        ].reset_index(drop=True)

        temp_amount = fund_amount

        subset_list = []

        for j in range(0, len(rebalancing_dates)):

            start_period = rebalancing_dates[j]

            if j == (len(rebalancing_dates) - 1):
                end_period = end_date
            else:
                end_period = rebalancing_dates[j + 1]

            subset_index = fund_index[fund_index["date"] >= start_period]
            subset_index = subset_index[subset_index["date"] <= end_period]

            for k in fund_codes:
                subset_index[k] = (
                    subset_index[k] / subset_index[k][subset_index.index[0]]
                )

            temp_df = backtest_funds(temp_amount, fund_codes, subset_index)
            # Getting the portfolio at the enddate
            temp_total = temp_df.iloc[(temp_df.shape[0] - 1)][fund_codes].sum()
            temp_amount = [temp_total * i for i in fund_percentage]
            temp_df["date"] = subset_index["date"]
            temp_df.drop(temp_df.tail(1).index, inplace=True)
            subset_list.append(temp_df)

        result_df = pd.concat(subset_list)
        result_df["date"] = result_df["date"].dt.strftime("%Y-%m-%d")

    else:
        result_df = backtest_funds(fund_amount, fund_codes, fund_index)
        result_df["date"] = dates

    result_df = result_df.drop(columns=fund_codes)

    result_df["drawdown"] = (
        result_df["portfolio"] - calculate_historical_max(result_df)
    ) / calculate_historical_max(result_df)

    return json.loads(result_df.to_json(orient="records"))
