import random
import time
from datetime import datetime

import httpx
import polars as pl

vanguard_funds = [
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
    "vanguard-ftse-uk-all-share-index-unit-trust-gbp-acc",
    "vanguard-ftse-100-index-unit-trust-gbp-acc",
    "vanguard-ftse-uk-equity-income-index-fund-gbp-acc",
    "vanguard-ftse-developed-europe-ex-uk-equity-index-fund-gbp-acc",
    "vanguard-ftse-developed-world-ex-uk-equity-index-fund-gbp-acc",
    "vanguard-ftse-global-all-cap-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
]

ire_funds = [
    "vanguard-emerging-markets-stock-index-fund-gbp-acc",
    "vanguard-euro-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-euro-investment-grade-bond-index-fund-gbp-hedged-acc",
    "vanguard-japan-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-japan-stock-index-fund-gbp-acc",
    "vanguard-pacific-ex-japan-stock-index-fund-gbp-acc",
    "vanguard-uk-government-bond-index-fund-gbp-acc",
    "vanguard-uk-investment-grade-bond-index-fund-gbp-acc",
    "vanguard-us-investment-grade-credit-index-fund-gbp-hedged-acc",
    "vanguard-us-government-bond-index-fund-gbp-hedged-acc",
]


def format_vanguard_returns(_monthly_returns: list[dict[str, str]], id: str) -> pl.DataFrame:
    """Format vanguard returns as polars dataframe."""
    monthly_returns = pl.from_dicts(_monthly_returns)
    monthly_returns = monthly_returns.with_columns(pl.lit(id).alias("id"))
    monthly_returns = monthly_returns.rename({"asOfDate": "date", "monthPercent": "monthly_return"})
    return monthly_returns


def main() -> None:
    """Download vanguard fund data."""
    url = "https://www.vanguardinvestor.co.uk/api/funds/{}"

    headers = {
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

    fields = [
        "id",
        "name",
        "assetClass",
        "inceptionDate",
        "currencyCode",
        "ticker",
        "OCF",
    ]

    _fund_details = []
    _fund_returns = []

    with httpx.Client(headers=headers) as client:
        # for fund in vanguard_funds + ire_funds:
        for fund in vanguard_funds[:1]:
            time.sleep(random.random() / 5)

            r = client.get(url.format(fund))
            fund_detail = {key: r.json()[key] for key in fields}
            _fund_details.append(fund_detail)

            fund_return = format_vanguard_returns(
                r.json()["fundData"]["annualNAVReturns"]["returns"], fund_detail["id"]
            )
            _fund_returns.append(fund_return)

    fund_returns = pl.concat(_fund_returns)
    fund_returns = fund_returns.with_columns(pl.col("date").cast(pl.Date).alias("date"))
    fund_returns = fund_returns.with_columns(pl.col("monthly_return") / 100.0)

    fund_details = pl.from_dicts(_fund_details)
    fund_details = fund_details.rename(
        {
            "assetClass": "asset_class",
            "inceptionDate": "inception_date",
            "currencyCode": "currency_code",
            "OCF": "ocf",
        }
    )
    fund_details = fund_details.with_columns(pl.col("inception_date").str.to_date("%d %B %Y"))

    current_year = datetime.now().year
    current_month = datetime.now().month

    date_returns = {
        "returns_ytd": datetime(current_year, 1, 1),
        "returns_1yr": datetime(current_year - 1, current_month, 1),
        "returns_3yr": datetime(current_year - 3, current_month, 1),
        "returns_5yr": datetime(current_year - 5, current_month, 1),
    }

    return_summaries = [
        (
            fund_returns.with_columns(pl.col("monthly_return") + 1.0)
            .filter(pl.col("date") > start_date)
            .group_by("id")
            .agg(pl.col("monthly_return").product().alias(col) - 1.0)
        )
        for col, start_date in date_returns.items()
    ]

    for i in return_summaries:
        fund_details = fund_details.join(i, how="left", on="id", coalesce=True)

    for col, start_date in date_returns.items():
        fund_details = fund_details.with_columns(
            pl.when(pl.col("inception_date") < start_date).then(pl.col(col)).otherwise(None).alias(col)
        )

    fund_returns = fund_returns.sort(by="date")

    fund_details.write_parquet("data/processed/fund_details.pq")
    fund_returns.write_parquet("data/processed/fund_returns.pq")


if __name__ == "__main__":
    main()
