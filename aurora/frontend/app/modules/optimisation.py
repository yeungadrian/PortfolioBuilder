from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from modules.funds import efficient_frontier, get_funds
from pydantic import BaseModel


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

    def efficient_frontier(self, efficient_portfolios, frontier_input):
        frontier_chart = (
            alt.Chart(efficient_portfolios)
            .mark_circle()
            .encode(
                x=alt.X("std", axis=alt.Axis(format="%")),
                y=alt.Y("returns", axis=alt.Axis(format="%")),
                tooltip=["returns", "std"] + frontier_input["funds"],
            )
        )
        st.subheader("Efficient Frontier")
        st.altair_chart(frontier_chart, use_container_width=True)

    def efficient_frontier_transition(self, efficient_portfolios, frontier_input):
        transition = pd.melt(
            efficient_portfolios,
            id_vars=["std", "returns"],
            value_name="Percentage",
            var_name="Ticker",
        )

        transition_chart = (
            alt.Chart(transition)
            .mark_area()
            .encode(
                x=alt.X("std", axis=alt.Axis(format="%")),
                y=alt.Y("Percentage:Q", stack="normalize", axis=alt.Axis(format="%")),
                color="Ticker:N",
                tooltip=["std", "Percentage", "Ticker"],
            )
        )

        st.subheader("Efficient Frontier Transition")
        st.altair_chart(transition_chart, use_container_width=True)

    def display(self):

        st.title("Portfolio Optimisation")
        fund_list = pd.DataFrame(get_funds())

        with st.form("my_form"):
            with st.sidebar:
                frontier_input = self.sidebar(fund_list)

                submitted = st.form_submit_button("Submit")

        if submitted:

            efficient_portfolios = pd.DataFrame(efficient_frontier(frontier_input))

            fund_weights = pd.DataFrame(
                efficient_portfolios["portfolio_weights"].tolist()
            )

            efficient_portfolios = pd.concat(
                [efficient_portfolios, fund_weights], axis=1
            ).drop(columns=["portfolio_weights"])

            self.efficient_frontier(efficient_portfolios, frontier_input)

            self.efficient_frontier_transition(efficient_portfolios, frontier_input)
