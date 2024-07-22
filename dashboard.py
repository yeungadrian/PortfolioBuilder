import json
from datetime import datetime

import altair as alt
import httpx
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ex-stream-ly Cool App", page_icon="🧊", layout="wide")

BASE_URL = "http://localhost:8000/"
BACKTEST_EXAMPLE = [
    {"amount": 100, "id": "vanguard-us-equity-index-fund-gbp-acc"},
    {"amount": 100, "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc"},
]


def screener_page() -> None:
    """Screener page."""
    r = httpx.get(f"{BASE_URL}funds/all/")
    df = pd.DataFrame(r.json())
    return_cols = df.columns[df.columns.str.contains("returns")].tolist()
    df = df.style.format({i: "{:,.2%}".format for i in return_cols})

    st.title("Fund Screener")
    st.dataframe(df)


def backtest_page() -> None:
    """Backtest page."""
    start_date = st.sidebar.date_input("Start date", value=datetime(2022, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    portfolio = st.sidebar.text_area("Portfolio setup", value=json.dumps(BACKTEST_EXAMPLE), height=400)
    r = httpx.post(
        f"{BASE_URL}backtest/",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "portfolio": json.loads(portfolio)},
    )

    st.title("Portfolio backtesting")

    detailed_holdings = []
    for i in r.json():
        _result = {}
        for holding in i["holdings"]:
            _result[holding["id"]] = holding["amount"]
        detailed_holdings.append(_result)

    df = pd.concat([pd.DataFrame(r.json())[["date", "portfolio_value"]], pd.DataFrame(detailed_holdings)], axis=1)
    df = df.melt(id_vars=["date", "portfolio_value"], var_name="fund", value_name="amount")
    chart = (
        alt.Chart(df)
        .mark_area()
        .encode(
            alt.X("date:T", axis=alt.Axis(format="%y %b", tickCount=12)),
            y="amount",
            color="fund:N",
            tooltip=["date:T", "amount", "fund", "portfolio_value"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


def main() -> None:
    """Streamlit dashboard."""
    page_index = st.sidebar.radio("Navigation", ["Screener", "Backtest", "Optimisation"])

    match page_index:
        case "Screener":
            screener_page()
        case "Backtest":
            backtest_page()


if __name__ == "__main__":
    main()
