from datetime import date
from typing import Any

import httpx
import polars as pl
from tqdm import tqdm

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
            "currencyCode",
            "ticker",
            "OCF",
            "managementType",
        ]
        self.fund_detail_mapping = {
            "id": "id",
            "name": "name",
            "assetClass": "asset_class",
            "inceptionDate": "inception_date",
            "currencyCode": "currency_code",
            "ticker": "ticker",
            "OCF": "ocf",
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

    def get_ids(self) -> list[Any]:
        """Get list of vanguard funds."""
        r = httpx.get(self.base_url + self.list_route, headers=self.headers)
        _fund_details = [{j: k for j, k in i.items() if j in self.fund_detail_keys} for i in r.json()]
        fund_details = pl.from_dicts(_fund_details)
        fund_details = fund_details.with_columns(pl.col("inceptionDate").cast(pl.Date)).filter(
            (pl.col("managementType") == "Index") & (pl.col("inceptionDate") <= self.min_inception_date)
        )
        ids: list[Any] = fund_details.select(pl.col("id")).to_series().to_list()
        return ids

    def format_details(self, response: Any) -> dict[str, str]:
        """Format fund details into dict."""
        fund_detail = {key: response[key] for key in self.fund_detail_keys}
        return fund_detail

    def format_returns(self, response: Any, id: str) -> pl.DataFrame:
        """Format monthly returns as polars dataframe."""
        _monthly_returns = response["fundData"]["annualNAVReturns"]["returns"]
        monthly_returns = pl.from_dicts(_monthly_returns)
        monthly_returns = monthly_returns.with_columns(pl.lit(id).alias("id"))
        monthly_returns = monthly_returns.rename({"asOfDate": "date", "monthPercent": "monthly_return"})
        return monthly_returns

    def download_all(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Download all data."""
        ids = self.get_ids()
        for id in tqdm(ids):
            response = self.request_data(self.base_url + self.detail_route.format(id))
            self._security_details.append(self.format_details(response))
            self._security_returns.append(self.format_returns(response, id))

        security_details = pl.from_dicts(self._security_details)
        security_details = security_details.rename(self.fund_detail_mapping)
        security_returns = pl.concat(self._security_returns)
        return security_details, security_returns
