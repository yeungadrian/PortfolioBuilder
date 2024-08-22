from datetime import datetime
from typing import Any

import altair as alt
import pandas as pd
import requests
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
    """Get available funds."""
    r = requests.get(f"{settings.base_url}funds/all/", timeout=settings.timeout)
    return r.json()


@st.cache_data(ttl="7d")
def backtest(start_date: str, end_date: str, portfolio: str) -> Any:
    """Backtest portfolio."""
    r = requests.post(
        f"{settings.base_url}backtest/",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "portfolio": portfolio},
        timeout=settings.timeout,
    )
    return r.json()


def convert_result_to_df(backtest_results: Any) -> pd.DataFrame:
    """Convert backtest result to dataframe."""
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
    return df


def backtest_line_chart(df: pd.DataFrame) -> alt.Chart:
    """Generate altair backtest line chart."""
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
    return chart


def main() -> None:
    """Backtest streamlit page."""
    available_funds = [i["id"] for i in get_funds()]
    # Sidebar
    start_date = st.sidebar.date_input("Start date", value=datetime(2017, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    ids = st.sidebar.multiselect("Select funds", options=available_funds, default=BACKTEST_IDS, max_selections=30)
    portfolio = [{"id": id, "amount": st.sidebar.number_input(label=id, value=100)} for id in ids]

    # Run backtest and format
    backtest_results = backtest(start_date, end_date, portfolio)
    df = convert_result_to_df(backtest_results)

    # Main page
    st.title("Portfolio Backtesting")
    st.subheader("Projection")
    if st.checkbox("Chart View", True):
        st.altair_chart(backtest_line_chart(df), use_container_width=True)
    else:
        st.dataframe(df)
    st.subheader("Metrics")
    metrics = pd.DataFrame(backtest_results["metrics"], index=[0])
    metrics = metrics.style.format("{:,.2%}")
    st.write(metrics)


main()
