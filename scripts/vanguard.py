from typing import Any

import httpx
import polars as pl


class Vanguard:
    """Vanguard asset manager helper."""

    def __init__(self) -> None:
        self.base_url = "https://www.vanguardinvestor.co.uk/api/funds/{}"
        self.fund_detail_keys = [
            "id",
            "name",
            "assetClass",
            "inceptionDate",
            "currencyCode",
            "ticker",
            "OCF",
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
            "Referer": "https://www.vanguardinvestor.co.uk/investments/vanguard-us-equity-index-fund-gbp-acc/price-performance",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }
        self._fund_details: list[dict[str, str]] = []
        self._fund_returns: list[pl.DataFrame] = []

    def request_data(self, url: str) -> Any:
        """Request data form asset manager."""
        with httpx.Client(headers=self.headers) as client:
            r = client.get(url)
            return r.json()

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

    def download_all(self, ids: list[str]) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Download all data."""
        for id in ids:
            response = self.request_data(self.base_url.format(id))

            self._fund_details.append(self.format_details(response))
            self._fund_returns.append(self.format_returns(response, id))

        fund_details = pl.from_dicts(self._fund_details)
        fund_details = fund_details.rename(self.fund_detail_mapping)
        fund_returns = pl.concat(self._fund_returns)

        return fund_details, fund_returns
