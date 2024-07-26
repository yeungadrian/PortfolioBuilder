import json
import os
from datetime import datetime
from typing import Any

import altair as alt
import httpx
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Portfolio Builder", page_icon="📊", layout="wide")

BASE_URL = os.getenv("BASE_API_URL", "http://localhost:8000/")
BACKTEST_EXAMPLE = [
    {"amount": 100, "id": "vanguard-us-equity-index-fund-gbp-acc"},
    {"amount": 100, "id": "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc"},
]
OPTIMISATION_IDS = [
    "vanguard-ftse-100-index-unit-trust-gbp-acc",
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
]


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get funds."""
    r = httpx.get(f"{BASE_URL}funds/all/")
    return r.json()


@st.cache_data(ttl="7d")
def backtest(start_date: str, end_date: str, portfolio: str) -> Any:
    """Get funds."""
    r = httpx.post(
        f"{BASE_URL}backtest/",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "portfolio": json.loads(portfolio)},
    )
    return r.json()


@st.cache_data(ttl="7d")
def get_efficient_fronter(start_date: str, end_date: str, ids: str, n_portfolios: int) -> Any:
    """Get funds."""
    r = httpx.post(
        f"{BASE_URL}optimisation/efficient-frontier?n_portfolios={n_portfolios}",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": json.loads(ids)},
    )
    return r.json()


def screener_page() -> None:
    """Screener page."""
    df = pd.DataFrame(get_funds())
    return_cols = df.columns[df.columns.str.contains("returns")].tolist()
    df = df.style.format({i: "{:,.2%}".format for i in return_cols})

    st.title("Fund Screener")
    st.dataframe(df)


def backtest_page() -> None:
    """Backtest page."""
    start_date = st.sidebar.date_input("Start date", value=datetime(2018, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    portfolio = st.sidebar.text_area("Portfolio setup", value=json.dumps(BACKTEST_EXAMPLE), height=400)

    backtest_results = backtest(start_date, end_date, portfolio)

    st.title("Portfolio Backtesting")

    detailed_holdings = []
    for i in backtest_results:
        _result = {}
        for holding in i["holdings"]:
            _result[holding["id"]] = holding["amount"]
        detailed_holdings.append(_result)

    df = pd.concat(
        [pd.DataFrame(backtest_results)[["date", "portfolio_value"]], pd.DataFrame(detailed_holdings)], axis=1
    )
    df = df.melt(id_vars=["date", "portfolio_value"], var_name="fund", value_name="amount")
    chart = (
        alt.Chart(df)
        .mark_area()
        .encode(
            alt.X("date:T", axis=alt.Axis(format="%b-%y ", tickCount=12)),
            y="amount",
            color="fund:N",
            tooltip=["date:T", "amount", "fund", "portfolio_value"],
        )
    )
    st.altair_chart(chart, use_container_width=True)


def optimisation_page() -> None:
    """Optimisation page."""
    n_portfolios = st.sidebar.number_input("Number of portfolios", min_value=30)
    start_date = st.sidebar.date_input("Start date", value=datetime(2018, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    ids = st.sidebar.text_area("Funds", value=json.dumps(OPTIMISATION_IDS), height=400)

    frontier = get_efficient_fronter(start_date, end_date, ids, n_portfolios)
    return_variance = pd.DataFrame(
        [
            {
                "expected_return": portfolio["expected_return"],
                "implied_standard_deviation": portfolio["implied_standard_deviation"],
            }
            for portfolio in frontier
        ]
    )
    portfolios = pd.concat(
        [pd.json_normalize(portfolio["portfolio"]).set_index("id").transpose() for portfolio in frontier]
    ).reset_index(drop=True)
    efficient_fronter = pd.concat([return_variance, portfolios], axis=1)

    frontier_chart = (
        alt.Chart(efficient_fronter)
        .mark_circle(size=80)
        .encode(
            x=alt.X(
                "implied_standard_deviation",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(zero=False),
            ),
            y=alt.Y(
                "expected_return",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(zero=False),
            ),
            tooltip=alt.Tooltip(
                efficient_fronter.columns.tolist(),
                format=".2%",
            ),
        )
    )

    st.title("Portfolio Optimisation")
    st.altair_chart(frontier_chart, use_container_width=True)


def main() -> None:
    """Streamlit dashboard."""
    page_index = st.sidebar.radio("Navigation", ["Screener", "Backtest", "Optimisation"])

    match page_index:
        case "Screener":
            screener_page()
        case "Backtest":
            backtest_page()
        case "Optimisation":
            optimisation_page()


if __name__ == "__main__":
    main()
