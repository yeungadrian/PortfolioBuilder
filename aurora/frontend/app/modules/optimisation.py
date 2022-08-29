from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from modules.funds import efficientFrontier, get_funds


def display_optimisation():

    st.title("Portfolio Optimisation")
    fund_list = pd.DataFrame(get_funds())

    st.sidebar.subheader("Optimisation inputs")

    start_date = st.sidebar.date_input(
        "Start Date", value=datetime(2017, 12, 31)
    ).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End Date", value=datetime(2020, 12, 31)).strftime(
        "%Y-%m-%d"
    )

    selected_funds = st.sidebar.multiselect(
        label="Fund selection",
        options=list(fund_list["Company"]),
        default=["Apple Inc.", "Amazon.com Inc."],
    )

    selected_fund_list = []

    for i in range(0, len(selected_funds)):
        selected_fund_list.append(
            fund_list[fund_list["Company"] == selected_funds[i]]["Code"].reset_index(
                drop=True
            )[0]
        )

    number_portfolios = st.sidebar.number_input(
        label="Number of portfolios", step=1, value=5
    )

    submit = st.sidebar.button(label="Run")

    if submit:

        frontier_input = {
            "start_date": start_date,
            "end_date": end_date,
            "funds": selected_fund_list,
            "num_portfolios": number_portfolios,
        }

        efficient_portfolios = pd.DataFrame(efficientFrontier(frontier_input))

        frontier_chart = (
            alt.Chart(efficient_portfolios)
            .mark_circle(size=20, color="green", opacity=0.6)
            .encode(
                x="std", y="returns", tooltip=["portfolioWeights", "returns", "std"]
            )
            .properties(width=700, height=400)
            .add_selection(alt.selection_interval(bind="scales"))
        )

        st.write("Efficient Frontier")
        st.write(frontier_chart)
