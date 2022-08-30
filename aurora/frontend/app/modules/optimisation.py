from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from modules.config import Config
from modules.data_loader import DataLoader
from pydantic import BaseModel

column_map = Config().column_map()
format_pct = Config().format_pct()
colors = Config().colors()


class Optimisation(BaseModel):
    def sidebar(self, fund_list):

        st.subheader("Optimisation inputs")

        start_date = st.date_input("Start Date", value=datetime(2017, 12, 31)).strftime(
            "%Y-%m-%d"
        )
        end_date = st.date_input("End Date", value=datetime(2020, 12, 31)).strftime(
            "%Y-%m-%d"
        )

        selected_funds = st.multiselect(
            label="Fund selection",
            options=list(fund_list["Company"]),
            default=["Apple Inc.", "Amazon.com Inc."],
        )

        selected_fund_list = []

        for i in range(0, len(selected_funds)):
            selected_fund_list.append(
                fund_list[fund_list["Company"] == selected_funds[i]][
                    "Code"
                ].reset_index(drop=True)[0]
            )

        number_portfolios = st.number_input(
            label="Number of portfolios", step=1, value=20
        )

        frontier_input = {
            "start_date": start_date,
            "end_date": end_date,
            "funds": selected_fund_list,
            "num_portfolios": number_portfolios,
        }
        return frontier_input

    def format_response(self, efficient_portfolios):
        fund_weights = pd.DataFrame(efficient_portfolios["portfolio_weights"].tolist())

        efficient_portfolios = pd.concat(
            [efficient_portfolios, fund_weights], axis=1
        ).drop(columns=["portfolio_weights"])

        return efficient_portfolios

    def best_sharpe_ratio(self, efficient_portfolios):
        best_portfolio = efficient_portfolios.iloc[
            efficient_portfolios["sharpe_ratio"].idxmax()
        ]

        st.subheader("Best Portfolio")
        best = pd.DataFrame(best_portfolio["portfolio_weights"], index=["Best"])
        best["returns"] = best_portfolio["returns"]
        best["std"] = best_portfolio["std"]
        best["sharpe_ratio"] = best_portfolio["sharpe_ratio"]

        best = best.rename(columns=column_map)

        st.dataframe(best.style.format({**format_pct}))

    def efficient_frontier(self, efficient_portfolios, frontier_input):

        std_min = round(efficient_portfolios["std"].min(), 3) - 0.005
        std_max = round(efficient_portfolios["std"].max(), 3) + 0.005

        returns_min = round(efficient_portfolios["returns"].min(), 3) - 0.005
        returns_max = round(efficient_portfolios["returns"].max(), 3) + 0.005

        efficient_portfolios = efficient_portfolios.rename(columns=column_map)

        frontier_chart = (
            alt.Chart(efficient_portfolios)
            .mark_circle()
            .encode(
                x=alt.X(
                    "Monthly standard deviation",
                    axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[std_min, std_max]),
                ),
                y=alt.Y(
                    "Monthly arithmetic mean",
                    axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[returns_min, returns_max]),
                ),
                color=alt.value(colors[0]),
                tooltip=alt.Tooltip(
                    ["Monthly arithmetic mean", "Monthly standard deviation"]
                    + frontier_input["funds"],
                    format=".2%",
                ),
            )
        )
        st.subheader("Efficient Frontier")
        st.altair_chart(frontier_chart, use_container_width=True)

    def efficient_frontier_transition(self, efficient_portfolios):
        transition = pd.melt(
            efficient_portfolios,
            id_vars=["std", "returns", "sharpe_ratio"],
            value_name="Percentage",
            var_name="Ticker",
        )

        std_min = transition["std"].min()
        std_max = transition["std"].max()

        transition = transition.rename(columns=column_map)

        transition_chart = (
            alt.Chart(transition)
            .mark_area()
            .encode(
                x=alt.X(
                    "Monthly standard deviation",
                    axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[std_min, std_max]),
                ),
                y=alt.Y("Percentage:Q", stack="normalize", axis=alt.Axis(format="%")),
                color=alt.Color("Ticker", scale=alt.Scale(range=colors)),
                tooltip=["Monthly standard deviation", "Percentage", "Ticker"],
            )
        )

        st.subheader("Efficient Frontier Transition")
        st.altair_chart(transition_chart, use_container_width=True)

    def display(self):

        st.title("Portfolio Optimisation")
        fund_list = pd.DataFrame(DataLoader().get_funds())

        with st.form("my_form"):
            with st.sidebar:
                frontier_input = self.sidebar(fund_list)

                submitted = st.form_submit_button("Submit")

        if submitted:

            efficient_portfolios = pd.DataFrame(
                DataLoader().efficient_frontier(frontier_input)
            )

            self.best_sharpe_ratio(efficient_portfolios)

            efficient_portfolios = self.format_response(efficient_portfolios)

            self.efficient_frontier(efficient_portfolios, frontier_input)

            self.efficient_frontier_transition(efficient_portfolios)
