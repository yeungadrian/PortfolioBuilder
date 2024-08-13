from datetime import datetime
from typing import Any

import altair as alt
import httpx
import numpy as np
import pandas as pd
import streamlit as st

from dashboard.config import settings

OPTIMISATION_IDS = [
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
    "vanguard-euro-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-ftse-100-index-unit-trust-gbp-acc",
    "vanguard-japan-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-japan-stock-index-fund-gbp-acc",
    "vanguard-uk-government-bond-index-fund-gbp-acc",
]


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get funds."""
    r = httpx.get(f"{settings.base_url}funds/all/", timeout=settings.timeout)
    return r.json()


@st.cache_data(ttl="7d")
def get_expected_returns(start_date: str, end_date: str, ids: str) -> Any:
    """Get expected returns."""
    r = httpx.post(
        f"{settings.base_url}optimisation/expected-returns",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    return r.json()


@st.cache_data(ttl="7d")
def get_risk_model(start_date: str, end_date: str, ids: str) -> Any:
    """Get risk model."""
    r = httpx.post(
        f"{settings.base_url}optimisation/risk-model?method=sample_cov",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    return r.json()


@st.cache_data(ttl="7d")
def get_efficient_fronter(start_date: str, end_date: str, ids: str, n_portfolios: int) -> Any:
    """Get efficient frontier."""
    r = httpx.post(
        f"{settings.base_url}optimisation/efficient-frontier?n_portfolios={n_portfolios}",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    return r.json()


def main() -> None:
    """Optimisation page."""
    available_funds = [i["id"] for i in get_funds()]
    n_portfolios = st.sidebar.number_input("Number of portfolios", value=40, max_value=250)
    start_date = st.sidebar.date_input("Start date", value=datetime(2017, 1, 1)).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End date", value=datetime(2024, 1, 1)).strftime("%Y-%m-%d")
    ids = st.sidebar.multiselect("Select funds", options=available_funds, default=OPTIMISATION_IDS, max_selections=30)

    individual_funds = pd.DataFrame(get_expected_returns(start_date, end_date, ids))
    risk_model = pd.DataFrame(get_risk_model(start_date, end_date, ids))
    individual_funds["implied_standard_deviation"] = np.sqrt(np.diag(risk_model.drop(columns="id").to_numpy()))

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

    individual_frontier_chart = (
        alt.Chart(individual_funds)
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
            tooltip=[
                alt.Tooltip(
                    "id:N",
                ),
                alt.Tooltip(
                    "expected_return:Q",
                    format=".2%",
                ),
                alt.Tooltip(
                    "implied_standard_deviation:Q",
                    format=".2%",
                ),
            ],
            color=alt.Color("id").scale(scheme="accent"),
        )
    )

    frontier_chart = (
        alt.Chart(efficient_fronter)
        .mark_circle(size=80, color="teal")
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
    if st.checkbox("Include individual funds"):
        frontier_chart = frontier_chart + individual_frontier_chart
    st.altair_chart(frontier_chart, use_container_width=True)

    with st.expander("Assumptions"):
        individual_funds = individual_funds.style.format(
            {i: "{:,.2%}".format for i in ["expected_return", "implied_standard_deviation"]}
        )
        st.write(individual_funds)


main()
