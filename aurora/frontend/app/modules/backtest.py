from datetime import datetime
from typing import List

import altair as alt
import pandas as pd
import requests
import streamlit as st
from modules.config import Config
from modules.funds import get_funds
from pydantic import BaseModel

column_map = Config().column_map()
format_pct = Config().format_pct()
format_dec = Config().format_dec()
colors = Config().colors()


class Backtest(BaseModel):
    short_metrics: List = [
        "cagr",
        "std_m",
        "max_drawdown",
        "sharpe_ratio",
        "sortino_ratio",
        "market_correlation",
    ]

    def sidebar(self):
        """Sidebar for streamlit page

        Returns:
            dict: Portfolio strategy inputs
        """

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

            backtest_input = {
                "start_date": start_date,
                "end_date": end_date,
                "portfolio": portfolio,
                "strategy": {"rebalance": rebalance, "rebalance_frequency": frequency},
            }

        return backtest_input

    @st.cache()
    def backtest_portfolio(self, input):
        """Backtest portfolio strategy

        Args:
            input (dict): portfolio strategy

        Returns:
            dict: portfolio backtest
        """

        url_backtest = "http://localhost:8000/backtest/"
        response = requests.post(url=url_backtest, json=input).json()

        return response

    def portfolio_value(self, portfolio_projection):
        """Display portfolio value section

        Args:
            portfolio_projection (dict): portfolio projection, value & metrics
        """
        backtest_portfolio = pd.DataFrame(portfolio_projection["projection"])
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
                color=alt.value(colors["fourth"]),
            )
        )

        st.altair_chart(value_chart, use_container_width=True)

    def summary_metrics(self, portfolio_projection):
        """Display summary metrics section. Title and table

        Args:
            portfolio_projection (_type_): _description_
        """
        metrics = portfolio_projection["metrics"]["metrics"]

        summary_metrics = {}

        for i in self.short_metrics:
            summary_metrics[i] = metrics[i]

        summary_metrics = pd.DataFrame(summary_metrics, index=[""])

        summary_metrics = summary_metrics.rename(columns=column_map)

        st.subheader("Summary metrics")

        st.markdown("")
        st.write(
            summary_metrics.style.format({**format_pct, **format_dec})
            .hide_index()
            .to_html(),
            unsafe_allow_html=True,
        )
        st.markdown("")

    def annual_return(self, portfolio_projection):
        """Annual return section, title, bar chart

        Args:
            portfolio_projection (dict): backtesting portfolio results
        """
        st.subheader("Annual returns")

        annual_returns = pd.DataFrame(
            portfolio_projection["metrics"]["annual"]["return"]
        )

        annual_returns = annual_returns.rename(
            columns={"portfolio_returns": "Portfolio returns", "date": "Date"}
        )

        return_chart = (
            alt.Chart(annual_returns)
            .mark_bar()
            .encode(
                x="Date:N",
                y=alt.Y("Portfolio returns", axis=alt.Axis(format="%")),
                tooltip=["Date:N", alt.Tooltip("Portfolio returns", format=".2%")],
                color=alt.value(colors["fourth"]),
            )
        )

        st.altair_chart(return_chart, use_container_width=True)

    def drawdowns(self, portfolio_projection):
        """Drawdown page, expander, title and line chart

        Args:
            portfolio_projection (dict): _description_
        """
        with st.expander("Drawdowns"):

            daily_drawdown = pd.DataFrame(
                portfolio_projection["metrics"]["daily"]["drawdown"]
            )

            daily_drawdown = daily_drawdown.rename(
                columns={"drawdown": "Daily drawdown", "date": "Date"}
            )

            drawdown_chart = (
                alt.Chart(daily_drawdown)
                .mark_line()
                .encode(
                    x="Date:T",
                    y=alt.Y("Daily drawdown", axis=alt.Axis(format="%")),
                    tooltip=["Date:T", alt.Tooltip("Daily drawdown", format=".2%")],
                    color=alt.value(colors["fourth"]),
                )
            )

            st.altair_chart(drawdown_chart, use_container_width=True)

    def metrics(self, portfolio_projection):
        """Full metrics, expander and table

        Args:
            portfolio_projection (dict): _description_
        """

        with st.expander("Metrics"):
            st.markdown("")
            pct_metrics = pd.DataFrame(
                portfolio_projection["metrics"]["metrics"], index=[0]
            ).rename(columns=column_map)
            pct_metrics = pct_metrics[format_pct.keys()]
            dec_metrics = pd.DataFrame(
                portfolio_projection["metrics"]["metrics"], index=[0]
            ).rename(columns=column_map)
            dec_metrics = dec_metrics[format_dec.keys()]

            col1, col2 = st.columns(2)
            with col1:
                st.write(
                    pct_metrics.transpose()
                    .style.format("{:.2%}")
                    .hide(axis="columns")
                    .to_html(),
                    unsafe_allow_html=True,
                )

            with col2:

                st.write(
                    dec_metrics.transpose()
                    .style.format("{:.2f}")
                    .hide(axis="columns")
                    .to_html(),
                    unsafe_allow_html=True,
                )
                st.markdown("")

    def display(self):
        """Display backtest page"""

        backtest_input = self.sidebar()

        st.title("Portfolio Backtesting")

        if len(backtest_input["portfolio"]):

            portfolio_projection = self.backtest_portfolio(backtest_input)

            self.portfolio_value(portfolio_projection)
            self.summary_metrics(portfolio_projection)
            self.annual_return(portfolio_projection)
            self.metrics(portfolio_projection)
            self.drawdowns(portfolio_projection)
