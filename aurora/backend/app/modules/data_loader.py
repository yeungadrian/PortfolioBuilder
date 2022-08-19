import json
from datetime import datetime, timedelta

import pandas as pd
import pyarrow.parquet as pq
from pydantic import BaseModel

config = {
    "fund_codes": "app/data/fundCodes.parquet",
    "fund_prices": "app/data/fundPrices.parquet",
    "ff_factors": "app/data/ffFactors.parquet",
    "sp500": "app/data/sp500.csv",
}


class DataLoader(BaseModel):
    def load_available_funds(self):
        all_funds = (
            pq.read_table(config["fund_codes"]).to_pandas().to_json(orient="records")
        )
        return json.loads(all_funds)

    def load_sp500(self, start_date, end_date):
        sp500 = pd.read_csv(config["sp500"], index_col=None)

        sp500 = sp500.rename(columns={"Date": "date", "Close/Last": "market"})
        sp500.date = pd.to_datetime(sp500.date)
        sp500 = sp500.sort_values(by="date").reset_index(drop=True)
        sp500 = self.backfill_ts(sp500, start_date, end_date, interpolation="fill")

        return sp500

    def backfill_ts(
        self, all_historical_data, start_date, end_date, interpolation=None
    ):
        subset_data = all_historical_data[all_historical_data["date"] >= start_date]
        subset_data = subset_data[subset_data["date"] <= end_date]
        subset_data = subset_data.sort_values("date").reset_index(drop=True)

        if interpolation == "fill":
            idx = pd.date_range(start_date, end_date)

            subset_data = subset_data.set_index("date")
            subset_data.index.name = None
            subset_data.index = pd.DatetimeIndex(subset_data.index)
            subset_data = subset_data.reindex(idx, fill_value=None)
            subset_data = subset_data.interpolate(
                method="linear", axis=0, limit_direction="both"
            )

            subset_data = subset_data.reset_index(drop=False)

            subset_data = subset_data.rename(
                columns={
                    "index": "date",
                }
            )

        return subset_data

    def load_historical_index(self, fund_codes, start_date, end_date):
        response_columns = ["date"] + fund_codes
        all_historical_prices = pq.read_table(
            "app/data/fundPrices.parquet", columns=response_columns
        ).to_pandas()

        subset_data = self.backfill_ts(
            all_historical_data=all_historical_prices,
            start_date=start_date,
            end_date=end_date,
            interpolation="fill",
        )

        subset_data.columns = response_columns

        return subset_data

    def load_ffFactors(
        self, regression_factors, start_date, end_date, frequency="daily"
    ):
        response_columns = ["date"] + regression_factors + ["RF"]
        data_location = "app/data/ffFactors.parquet"

        if frequency == "monthly":
            data_location = "app/data/ffFactorsMonthly.parquet"

        all_historical_factors = pq.read_table(
            data_location, columns=response_columns
        ).to_pandas()
        subset_data = self.backfill_ts(
            all_historical_data=all_historical_factors,
            start_date=start_date,
            end_date=end_date,
            interpolation=None,
        )

        # Kenneth French's data is off by factor of 100
        for k in response_columns:
            if k != "date":
                subset_data[k] = subset_data[k] / 100

        subset_data.columns = response_columns

        return json.loads(subset_data.to_json(orient="records"))

    def prepare_data(self, timeseries):
        timeseries["date"] = pd.to_datetime(timeseries["date"])
        timeseries = timeseries.sort_values(by="date").reset_index(drop=True)

        return timeseries


def load_available_funds():
    all_funds = (
        pq.read_table("app/data/fundCodes.parquet")
        .to_pandas()
        .to_json(orient="records")
    )

    return json.loads(all_funds)


def tidy_timeseries_data(all_historical_data, start_date, end_date, interpolation=None):
    subset_data = all_historical_data[all_historical_data["date"] >= start_date]
    subset_data = subset_data[subset_data["date"] <= end_date]
    subset_data = subset_data.sort_values("date").reset_index(drop=True)

    if interpolation == "fill":
        idx = pd.date_range(start_date, end_date)

        subset_data = subset_data.set_index("date")
        subset_data.index.name = None
        subset_data.index = pd.DatetimeIndex(subset_data.index)
        subset_data = subset_data.reindex(idx, fill_value=None)
        subset_data = subset_data.interpolate(
            method="linear", axis=0, limit_direction="both"
        )

        subset_data = subset_data.reset_index(drop=False)

    return subset_data


def load_historical_index(fund_codes, start_date, end_date):
    response_columns = ["date"] + fund_codes
    all_historical_prices = pq.read_table(
        "app/data/fundPrices.parquet", columns=response_columns
    ).to_pandas()

    subset_data = tidy_timeseries_data(
        all_historical_data=all_historical_prices,
        start_date=start_date,
        end_date=end_date,
        interpolation="fill",
    )

    subset_data.columns = response_columns
    subset_data["date"] = subset_data["date"].dt.strftime("%Y-%m-%d")

    return json.loads(subset_data.to_json(orient="records"))


def load_normalised_historical_index(fund_codes, start_date, end_date):
    response_columns = ["date"] + fund_codes

    subset_data = pd.DataFrame(
        load_historical_index(
            fund_codes=fund_codes, start_date=start_date, end_date=end_date
        )
    )

    for i in fund_codes:
        subset_data[f"{i}index"] = subset_data[i] / subset_data[i][0]

    subset_data = subset_data.fillna(0)
    subset_data = subset_data.drop(fund_codes, axis=1)
    subset_data.columns = response_columns

    return json.loads(subset_data.to_json(orient="records"))


def load_historical_returns(fund_codes, start_date, end_date, frequency):
    response_columns = ["date"] + fund_codes

    start_date = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
    start_date = datetime.strftime(start_date, "%Y-%m-%d")

    subset_data = pd.DataFrame(
        load_historical_index(
            fund_codes=fund_codes, start_date=start_date, end_date=end_date
        )
    )

    if frequency == "monthly":
        subset_data["date"] = pd.to_datetime(subset_data["date"])
        subset_data = subset_data[subset_data["date"].dt.is_month_end].reset_index(
            drop=True
        )
        subset_data["date"] = subset_data["date"].dt.strftime("%Y-%m-%d")

    for i in fund_codes:
        subset_data[f"{i}index"] = (subset_data[i] / subset_data[i].shift()) - 1

    subset_data = subset_data.dropna()
    subset_data = subset_data.drop(fund_codes, axis=1)
    subset_data.columns = response_columns

    return json.loads(subset_data.to_json(orient="records"))


def load_ffFactors(regression_factors, start_date, end_date, frequency="daily"):
    response_columns = ["date"] + regression_factors + ["RF"]
    data_location = "app/data/ffFactors.parquet"

    if frequency == "monthly":
        data_location = "app/data/ffFactorsMonthly.parquet"

    all_historical_factors = pq.read_table(
        data_location, columns=response_columns
    ).to_pandas()
    subset_data = tidy_timeseries_data(
        all_historical_data=all_historical_factors,
        start_date=start_date,
        end_date=end_date,
        interpolation=None,
    )

    # Kenneth French's data is off by factor of 100
    for k in response_columns:
        if k != "date":
            subset_data[k] = subset_data[k] / 100

    subset_data.columns = response_columns

    return json.loads(subset_data.to_json(orient="records"))
