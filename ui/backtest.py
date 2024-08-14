from datetime import datetime
from typing import Any

import altair as alt
import httpx
import pandas as pd
import streamlit as st

from ui.config import settings

BACKTEST_IDS = [
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
    "vanguard-ftse-100-index-unit-trust-gbp-acc",
    "vanguard-japan-stock-index-fund-gbp-acc",
]


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get funds."""
    r = httpx.get(f"{settings.base_url}funds/all/", timeout=settings.timeout)
    return r.json()


@st.cache_data(ttl="7d")
def backtest(start_date: str, end_date: str, portfolio: str) -> Any:
    """Backtest portfolio."""
    r = httpx.post(
        f"{settings.base_url}backtest/",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "portfolio": portfolio},
        timeout=settings.timeout,
    )
    return r.json()


def main() -> None:
    """Backtest page."""
    available_funds = [i["id"] for i in get_funds()]
    start_date = st.sidebar.date_input("Start date", value=datetime(2017, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    ids = st.sidebar.multiselect("Select funds", options=available_funds, default=BACKTEST_IDS, max_selections=30)
    portfolio = [{"id": id, "amount": st.sidebar.number_input(label=id, value=100)} for id in ids]

    backtest_results = backtest(start_date, end_date, portfolio)

    st.title("Portfolio Backtesting")

    detailed_holdings = []
    for i in backtest_results["projection"]:
        _result = {}
        for holding in i["holdings"]:
            _result[holding["id"]] = holding["amount"]
        detailed_holdings.append(_result)

    df = pd.concat(
        [pd.DataFrame(backtest_results["projection"])[["date", "portfolio_value"]], pd.DataFrame(detailed_holdings)],
        axis=1,
    )
    df = df.melt(id_vars=["date", "portfolio_value"], var_name="fund", value_name="amount")

    chart = (
        alt.Chart(df)
        .mark_area()
        .encode(
            alt.X("date:T", axis=alt.Axis(format="%b-%y ", tickCount=12)),
            y="amount",
            color=alt.Color("fund:N").scale(scheme="teals"),
            tooltip=["date:T", "amount", "fund", "portfolio_value"],
        )
    )
    st.subheader("Projection")
    if st.checkbox("Chart View", True):
        st.altair_chart(chart, use_container_width=True)
    else:
        st.dataframe(df.pivot_table(index=["date", "portfolio_value"], columns=["fund"], values="amount"))
    st.subheader("Metrics")
    metrics = pd.DataFrame(backtest_results["metrics"], index=[0])
    metrics = metrics.style.format("{:,.2%}")
    st.write(metrics)


main()
