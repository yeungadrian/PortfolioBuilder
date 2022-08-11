from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st
from modules.funds import get_funds


def sidebar():
    st.title("Portfolio Backtesting")
    fund_list = pd.DataFrame(get_funds())

    st.sidebar.subheader("Portfolio inputs")

    start_date = st.sidebar.date_input(
        "Start Date", value=datetime(2010, 12, 31)
    ).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End Date", value=datetime(2020, 12, 31)).strftime(
        "%Y-%m-%d"
    )

    rebalance_options = {"Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}

    rebalance = st.sidebar.checkbox("Rebalance portfolio")
    if rebalance:
        rebalance_frequency = st.sidebar.selectbox(
            label="Rebalance frequency", options=list(rebalance_options.keys())
        )
        frequency = rebalance_options[rebalance_frequency]
    else:
        frequency = None

    selected_funds = st.sidebar.multiselect(
        label="Fund selection",
        options=list(fund_list["Company"]),
        default=["Apple Inc."],
    )
    portfolio = []
    amount_list = {}
    for i in range(0, len(selected_funds)):
        amount_list[f"fund{i}"] = st.sidebar.number_input(
            label=f"{selected_funds[i]}", key=i, value=1000
        )

    for i in range(0, len(selected_funds)):
        portfolio.append(
            {
                "fund": fund_list[fund_list["Company"] == selected_funds[i]][
                    "Code"
                ].reset_index(drop=True)[0],
                "amount": amount_list[f"fund{i}"],
            }
        )

    return start_date, end_date, frequency, portfolio, rebalance


def display_backtest():

    # Portfolio Backtesting

    start_date, end_date, frequency, portfolio, rebalance = sidebar()

    # Portfolio Historical Projection

    if len(portfolio):
        backtest_input = {
            "start_date": start_date,
            "end_date": end_date,
            "portfolio": portfolio,
            "strategy": {"rebalance": rebalance, "rebalance_frequency": frequency},
        }

        url_backtest = "http://localhost:8000/backtest/"
        backtest_response = requests.post(url=url_backtest, json=backtest_input).json()

        backtest_portfolio = pd.DataFrame(backtest_response["projection"])
        backtest_portfolio["date"] = pd.to_datetime(backtest_portfolio["date"])

        chartoutput = (
            alt.Chart(backtest_portfolio)
            .mark_line()
            .encode(x="date", y="portfolio")
            .properties(width=700)
        )

        st.write(chartoutput)

        with st.expander(label="Metrics"):
            cagr = round(backtest_response["metrics"]["cagr"], 2) * 100
            monthly_std = round(backtest_response["metrics"]["std_m"], 2) * 100
            downside_std = (
                round(backtest_response["metrics"]["std_downside_m"], 2) * 100
            )
            sharpe_ratio = round(backtest_response["metrics"]["sharpe_ratio"], 2)
            sortino_ratio = round(backtest_response["metrics"]["sortino_ratio"], 2)
            max_drawdown = round(backtest_response["metrics"]["max_drawdown"], 2) * 100

            st.markdown(
                f"""
                | Metric | Value |
                | ------ | ----- |
                |Compound Annual Growth Rate:| {cagr}% |
                |Monthly Std:| {monthly_std}% |
                |Downside Std:| {downside_std}% |
                |Sharpe Ratio:| {sharpe_ratio} |
                |Sortino Ratio:| {sortino_ratio} |
                |Max Drawdown:| {max_drawdown}% |
                """
            )
