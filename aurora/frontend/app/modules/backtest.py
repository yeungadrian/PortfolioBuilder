from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st
from modules.funds import get_funds

summary_map = {
    "cagr": "CAGR",
    "std_m": "Monthly standard deviation",
    "max_drawdown": "Maximum drawdown",
    "sharpe_ratio": "Sharpe ratio",
    "sortino_ratio": "Sortino ratio",
    "market_correlation": "Market correlation",
}

metric_map = {
    "cagr": "CAGR",
    "std_m": "Monthly standard deviation",
    "max_drawdown": "Maximum drawdown",
    "sharpe_ratio": "Sharpe ratio",
    "sortino_ratio": "Sortino ratio",
    "market_correlation": "Market correlation",
    "arithmetic_mean_m": "Monthly Arithmetic mean",
    "arithmetic_mean_y": "Monthly Arithmetic mean",
    "geometric_mean_m": "Monthly Arithmetic mean",
    "geometric_mean_y": "Monthly Arithmetic mean",
    "std_m": "Monthly standard deviation",
    "std_downside_m": "Monthly downside standard deviation",
    "alpha": "Alpha",
    "beta": "Beta",
    "r_squared": "R squared",
    "cagr": "CAGR",
    "treynor_ratio": "Treynor ratio",
    "calmar_ratio": "Calmar ratio",
    "active_return": "Active return",
    "tracking_error": "Tracking error",
    "information_ratio": "Information ratio",
    "upside_capture_ratio": "Upside capture ratio",
    "downside_capture_ratio": "Downside capture ratio",
    "capture_ratio": "Capture ratio",
}

format_dict = {
    "Maximum drawdown": "{:.2%}",
    "Monthly standard deviation": "{:.2%}",
    "Annual arithmetic mean": "{:.2%}",
    "Monthly arithmetic mean": "{:.2%}",
    "CAGR": "{:.2%}",
    "Sharpe ratio": "{:.2f}",
    "Sortino ratio": "{:.2f}",
    "Market correlation": "{:.2f}",
}

colors = {
    "first": "#ED254E",
    "second": "#1E2019",
    "third": "#361D2E",
    "fourth": "#3C6997",
    "fifth": "#EEE2DF",
}


class Backtest:
    def sidebar(self):

        available_funds = pd.DataFrame(get_funds())

        st.sidebar.subheader("Portfolio inputs")

        start_date = st.sidebar.date_input(
            "Start Date", value=datetime(2010, 12, 31)
        ).strftime("%Y-%m-%d")
        end_date = st.sidebar.date_input(
            "End Date", value=datetime(2020, 12, 31)
        ).strftime("%Y-%m-%d")

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
            options=list(available_funds["Company"]),
            default=["Apple Inc."],
        )
        portfolio = []
        amounts = {}
        for i in range(0, len(selected_funds)):
            amounts[f"fund{i}"] = st.sidebar.number_input(
                label=f"{selected_funds[i]}", key=i, value=1000
            )

            portfolio.append(
                {
                    "fund": available_funds.loc[
                        available_funds["Company"] == selected_funds[i]
                    ]["Code"].reset_index(drop=True)[0],
                    "amount": amounts[f"fund{i}"],
                }
            )

        return start_date, end_date, frequency, portfolio, rebalance

    @st.cache()
    def get_backtest(self, backtest_input):
        url_backtest = "http://localhost:8000/backtest/"
        backtest_response = requests.post(url=url_backtest, json=backtest_input).json()

        return backtest_response

    def portfolio_value_page(self, backtest_response):
        backtest_portfolio = pd.DataFrame(backtest_response["projection"])
        backtest_portfolio["date"] = pd.to_datetime(backtest_portfolio["date"])

        backtest_portfolio = backtest_portfolio.rename(
            columns={"portfolio": "Portfolio Value ($)", "date": "Date"}
        )

        st.subheader("Portfolio value")

        value_chart = (
            alt.Chart(backtest_portfolio)
            .mark_line()
            .encode(
                x="Date",
                y="Portfolio Value ($)",
                tooltip=["Date", "Portfolio Value ($)"],
                color=alt.value(colors["first"]),
            )
        )

        st.altair_chart(value_chart, use_container_width=True)

    def summary_metrics_page(self, backtest_response):
        metrics = backtest_response["metrics"]["metrics"]

        summary_metrics = {}

        for i in summary_map.keys():
            summary_metrics[i] = metrics[i]

        summary_metrics = pd.DataFrame(summary_metrics, index=[""])

        summary_metrics = summary_metrics.rename(columns=summary_map)

        st.subheader("Summary metrics")

        st.markdown("")
        st.write(
            summary_metrics.style.format(format_dict).hide_index().to_html(),
            unsafe_allow_html=True,
        )
        st.markdown("")

    def annual_return(self, backtest_response):
        st.subheader("Annual returns")

        annual_returns = pd.DataFrame(backtest_response["metrics"]["annual"]["return"])

        return_chart = (
            alt.Chart(annual_returns)
            .mark_bar()
            .encode(
                x="date:T",
                y=alt.Y("portfolio_returns", axis=alt.Axis(format="%")),
                tooltip=["date:T", alt.Tooltip("portfolio_returns", format=".2%")],
                color=alt.value(colors["second"]),
            )
        )

        st.altair_chart(return_chart, use_container_width=True)

    def drawdowns(self, backtest_response):
        with st.expander("Drawdowns"):

            daily_drawdown = pd.DataFrame(
                backtest_response["metrics"]["daily"]["drawdown"]
            )

            drawdown_chart = (
                alt.Chart(daily_drawdown)
                .mark_line()
                .encode(
                    x="date:T",
                    y=alt.Y("drawdown", axis=alt.Axis(format="%")),
                    tooltip=["date:T", alt.Tooltip("drawdown", format=".2%")],
                    color=alt.value(colors["fourth"]),
                )
            )

            st.altair_chart(drawdown_chart, use_container_width=True)

    def metrics(self, backtest_response):
        with st.expander("Metrics"):
            st.markdown("")
            st.write(
                pd.DataFrame(backtest_response["metrics"]["metrics"], index=[0])
                .rename(columns=metric_map)
                .transpose()
                .reset_index()
                .style.format(format_dict)
                .hide_index()
                .hide_columns()
                .to_html(),
                unsafe_allow_html=True,
            )
            st.markdown("")

    def display(self):

        start_date, end_date, frequency, portfolio, rebalance = self.sidebar()

        st.title("Portfolio Backtesting")

        if len(portfolio):
            backtest_input = {
                "start_date": start_date,
                "end_date": end_date,
                "portfolio": portfolio,
                "strategy": {"rebalance": rebalance, "rebalance_frequency": frequency},
            }

            backtest_response = self.get_backtest(backtest_input)

            self.portfolio_value_page(backtest_response)

            self.summary_metrics_page(backtest_response)

            self.annual_return(backtest_response)

            self.metrics(backtest_response)

            self.drawdowns(backtest_response)
