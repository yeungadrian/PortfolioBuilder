from datetime import date
from typing import Any

import httpx
import polars as pl
from tqdm import tqdm

from app.schemas import SecurityDetails
from scripts.base import Manager


class Vanguard(Manager):
    """Vanguard asset manager helper."""

    def __init__(self, min_inception_date: date) -> None:
        self.base_url = "https://www.vanguardinvestor.co.uk"
        self.list_route = "/api/productList"
        self.detail_route = "/api/funds/{}"
        self.fund_detail_keys = [
            "id",
            "name",
            "assetClass",
            "inceptionDate",
            "sedol",
            "ocfValue",
            "managementType",
            "shareClass",
        ]
        self.fund_detail_mapping = {
            "id": "id",
            "name": "name",
            "assetClass": "asset_class",
            "inceptionDate": "inception_date",
            "sedol": "sedol",
            "ocfValue": "ocf",
        }
        self.headers = {
            "Host": "www.vanguardinvestor.co.uk",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }
        self.min_inception_date = min_inception_date
        self._security_details: list[dict[str, str]] = []
        self._security_returns: list[pl.DataFrame] = []

    def request_data(self, url: str) -> Any:
        """Request data form asset manager."""
        with httpx.Client(headers=self.headers) as client:
            r = client.get(url)
            return r.json()

    def get_fund_details(self) -> pl.DataFrame:
        """Get list of vanguard funds."""
        r = httpx.get(self.base_url + self.list_route, headers=self.headers)
        _fund_details = [{j: k for j, k in i.items() if j in self.fund_detail_keys} for i in r.json()]
        fund_details = pl.from_dicts(_fund_details)
        fund_details = fund_details.rename(self.fund_detail_mapping)
        fund_details = fund_details.cast({"inception_date": pl.Date, "ocf": str})
        fund_details = fund_details.filter(
            (pl.col("managementType") == "Index")
            & (pl.col("inception_date") <= self.min_inception_date)
            & (pl.col("shareClass") == "Accumulation")
        )
        return fund_details

    def format_details(self, fund_details: pl.DataFrame) -> Any:
        """Format fund details into dict."""
        fund_detail = fund_details.to_dicts()[0]
        SecurityDetails.model_validate(fund_detail)
        return fund_detail

    def format_returns(self, response: Any, id: str) -> pl.DataFrame:
        """Format monthly returns as polars dataframe."""
        _monthly_returns = response["fundData"]["annualNAVReturns"]["returns"]
        monthly_returns = pl.from_dicts(_monthly_returns)
        monthly_returns = monthly_returns.with_columns(pl.lit(id).alias("id"))
        monthly_returns = monthly_returns.rename({"asOfDate": "date", "monthPercent": "monthly_return"})
        monthly_returns = monthly_returns.cast({"date": pl.Date, "monthly_return": pl.Float64})
        monthly_returns = monthly_returns.sort(by="date")
        monthly_returns = monthly_returns.with_columns(pl.col("monthly_return") / 100.0)
        return monthly_returns

    def download_all(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Download all data."""
        fund_details = self.get_fund_details()
        ids = fund_details.select(pl.col("id")).to_series().to_list()
        for id in tqdm(ids):
            response = self.request_data(self.base_url + self.detail_route.format(id))
            self._security_details.append(self.format_details(fund_details.filter(pl.col("id") == id)))
            self._security_returns.append(self.format_returns(response, id))
        security_details = pl.from_dicts(self._security_details)
        security_returns = pl.concat(self._security_returns)
        return security_details, security_returns
