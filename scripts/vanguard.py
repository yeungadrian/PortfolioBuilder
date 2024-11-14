from datetime import date
from typing import Any

import httpx
import polars as pl
from tqdm import tqdm


class Vanguard:
    """Vanguard asset manager helper."""

    def __init__(self, min_inception_date: date) -> None:
        self.min_inception_date = min_inception_date
        self.base_url = "https://www.vanguardinvestor.co.uk"
        self.list_route = "/api/productList"
        self.detail_route = "/api/funds/{}"
        self._security_returns: list[pl.DataFrame] = []

    def request_data(self, url: str) -> Any:
        """Request data form asset manager."""
        with httpx.Client(
            headers={
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
        ) as client:
            r = client.get(url)
            return r.json()

    def get_fund_details(self) -> pl.DataFrame:
        """Get list of vanguard funds that meet criteria."""
        r = self.request_data(self.base_url + self.list_route)
        fund_details = pl.from_dicts(
            r,
            schema={
                "id": str,
                "name": str,
                "inceptionDate": str,
                "assetClass": str,
                "sedol": str,
                "ocfValue": str,
                "managementType": str,
                "shareClass": str,
            },
        )
        fund_details = fund_details.cast({"inceptionDate": pl.Date})
        fund_details = fund_details.rename(
            {
                "assetClass": "asset_class",
                "inceptionDate": "inception_date",
                "ocfValue": "ocf",
                "managementType": "management_type",
                "shareClass": "share_class",
            }
        )
        fund_details = fund_details.filter(
            (pl.col("management_type") == "Index")
            & (pl.col("inception_date") <= self.min_inception_date)
            & (pl.col("share_class") == "Accumulation")
        )
        fund_details = fund_details.drop(["management_type", "share_class"])
        return fund_details

    def format_returns(self, response: Any, id: str) -> pl.DataFrame:
        """Format monthly returns as polars dataframe."""
        monthly_returns = pl.from_dicts(
            response["fundData"]["annualNAVReturns"]["returns"],
            schema={"asOfDate": str, "monthPercent": pl.Float64},
        )
        monthly_returns = monthly_returns.cast({"asOfDate": pl.Date})
        monthly_returns = monthly_returns.rename(
            {
                "asOfDate": "date",
                "monthPercent": "monthly_return",
            }
        )
        monthly_returns = monthly_returns.sort(by="date")
        monthly_returns = monthly_returns.with_columns(pl.lit(id).alias("id"))
        monthly_returns = monthly_returns.with_columns(pl.col("monthly_return").truediv(100.0))
        return monthly_returns

    def download_all(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Download all data."""
        security_details = self.get_fund_details()
        ids = security_details.select(pl.col("id")).to_series().to_list()
        for id in tqdm(ids, desc="Vanguard"):
            r = self.request_data(self.base_url + self.detail_route.format(id))
            self._security_returns.append(self.format_returns(r, id))
        security_returns = pl.concat(self._security_returns)
        return security_details, security_returns
