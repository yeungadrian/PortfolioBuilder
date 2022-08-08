import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

from modules.funds import get_funds, backtest


def display_backtest():

    # Portfolio Backtesting

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

    # Portfolio Historical Projection

    if len(portfolio):
        backtest_input = {
            "startDate": start_date,
            "endDate": end_date,
            "portfolio": portfolio,
            "strategy": {"rebalance": rebalance, "rebalanceFrequency": frequency},
        }

        backtest_response = backtest(backtest_input)

        backtest_portfolio = pd.DataFrame(backtest_response["projection"])
        backtest_portfolio["date"] = pd.to_datetime(backtest_portfolio["date"])
        backtest_monthly_returns = pd.DataFrame(
            backtest_response["metrics"]["monthlyReturns"]
        )
        backtest_monthly_returns["date"] = pd.to_datetime(
            backtest_monthly_returns["date"]
        )

        chartoutput = (
            alt.Chart(backtest_portfolio)
            .mark_line()
            .encode(x="date", y="portfolio")
            .properties(width=700)
        )

        st.write(chartoutput)

        with st.expander(label="Metrics"):
            cagr = round(backtest_response["metrics"]["cagr"], 2) * 100
            monthly_std = round(backtest_response["metrics"]["monthly_std"], 2) * 100
            downside_std = round(backtest_response["metrics"]["downside_std"], 2) * 100
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

        with st.expander(label="Monthly returns"):
            monthly_return_chart = (
                alt.Chart(backtest_monthly_returns)
                .mark_bar()
                .encode(x="date", y="monthlyReturn")
                .properties(width=700)
            )

            st.write(monthly_return_chart)

        with st.expander(label="Daily drawdown"):
            monthly_return_chart = (
                alt.Chart(pd.DataFrame(backtest_portfolio))
                .mark_line()
                .encode(x="date", y="drawdown")
                .properties(width=700)
            )

            st.write(monthly_return_chart)
