import re
from datetime import date
from pathlib import Path

import httpx
import polars as pl
from bs4 import BeautifulSoup


def main() -> None:
    """Download ishares fund data."""
    df = pl.read_csv("../data/raw/ishares.csv")
    df = df.rename(
        {
            "Fund Name": "name",
            "Asset Class": "asset_class",
            "Inception Date": "inception_date",
            "Share Class Currency": "currency_code",
            "Ticker": "ticker",
            "Key Facts": "ocf",
        }
    )

    with Path("../data/raw/ishares.html").open("rb") as f:
        soup = BeautifulSoup(f)

    table = soup.findAll("table")[0]
    rows = []
    for n, row in enumerate(table.findAll("tr")[1:]):
        tag = "td"
        items = row.findAll(tag)
        texts = []
        for m, item in enumerate(items[0:2]):
            if (m == 1) & (n > 0):
                texts.append(item.a["href"])
            else:
                texts.append(item.text)
        rows.append(texts)

    _ticker_id_mapping = [i for i in rows if i[0] in df["ticker"].to_list()]
    ticker_id_mapping = pl.DataFrame(_ticker_id_mapping).transpose()
    ticker_id_mapping.columns = ["ticker", "id"]

    headers = {
        "Host": "www.ishares.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.ishares.com/uk/individual/en/products/229111/blackrock-blk-us-index-sub-fund-flex-acc-usd-fund",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "TE": "trailers",
    }

    _fund_returns: list[pl.DataFrame] = []
    for id in df["id"].to_list():
        id = id.replace("/uk/individual/en/products/", "")
        _ids = id.split("/")
        code = _ids[0]
        id = _ids[1]

        url = f"https://www.ishares.com/uk/individual/en/products/{code}/{id}/1506575576005.ajax"

        with httpx.Client(headers=headers) as client:
            r = client.get(url)

        perf_pattern = "var performanceData = (.+);\nvar"
        _performance_data = re.findall(perf_pattern, r.content.decode("utf-8"))[0]

        date_pattern = r"Date.UTC\((.+?)\),y"
        dates = re.findall(date_pattern, _performance_data)

        value_pattern = r"y:Number\(\((.+?)\).toFixed"
        values = re.findall(value_pattern, _performance_data)

        dates = [date(int(i[0]), int(i[1]) + 1, int(i[2])) for _date in dates for i in [_date.split(",")]]

        fund_returns = pl.DataFrame({"date": dates, "value": values})

        fund_returns = (
            fund_returns.with_columns(
                pl.col("value").cast(pl.Float64),
            )
            .with_columns((pl.col("value") / pl.col("value").shift(1) - 1).alias("monthly_return"))
            .drop(pl.col("value"))
            .filter(pl.col("monthly_return").is_not_null())
        )

        fund_returns = fund_returns.with_columns(pl.lit(id).alias("id"))

    df = df.join(ticker_id_mapping, on="ticker")
    df.write_parquet("../data/processed/ishares_details.pq")
