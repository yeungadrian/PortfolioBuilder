"""Module for optimisation page."""

from datetime import date
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
from config import settings

OPTIMISATION_IDS = [
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
    "vanguard-japan-stock-index-fund-gbp-acc",
    "vanguard-uk-government-bond-index-fund-gbp-acc",
]


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get available funds."""
    r = requests.get(f"{settings.base_url}{settings.securities_path}", timeout=settings.timeout)
    return r.json()


@st.cache_data(ttl="7d")
def get_expected_returns(start_date: str, end_date: str, ids: list[str]) -> Any:
    """Get expected returns."""
    r = requests.post(
        f"{settings.base_url}{settings.expected_return_path}",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl="7d")
def get_risk_model(start_date: str, end_date: str, ids: list[str]) -> Any:
    """Get risk model."""
    r = requests.post(
        f"{settings.base_url}{settings.risk_model_path}",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl="7d")
def get_efficient_fronter(start_date: str, end_date: str, ids: list[str], n_portfolios: int) -> Any:
    """Get efficient frontier for set of funds."""
    r = requests.post(
        f"{settings.base_url}{settings.efficient_fronter_path}?n_portfolios={n_portfolios}",
        headers={"Content-Type": "application/json"},
        json={"start_date": start_date, "end_date": end_date, "ids": ids},
        timeout=settings.timeout,
    )
    r.raise_for_status()
    return r.json()


def ef_scatter_plot(efficient_fronter: pd.DataFrame) -> alt.Chart:
    """Create efficient frontier scatter_plot."""
    return (
        alt.Chart(efficient_fronter)
        .mark_circle(size=80, color=settings.color_primary)
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


def scatter_plot(individual_funds: pd.DataFrame) -> alt.Chart:
    """Risk return plot for all individual funds."""
    return (
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


def main() -> None:
    """Optimisation page."""
    available_funds = [i["id"] for i in get_funds()]

    # Sidebar
    n_portfolios = st.sidebar.number_input("Number of portfolios", value=40, max_value=250)
    _start_date = st.sidebar.date_input("Start date", value=date(2017, 1, 1))
    if isinstance(_start_date, date):
        start_date = _start_date.strftime("%Y-%m-%d")
    else:
        raise ValueError()
    _end_date = st.sidebar.date_input("End date", value=date(2024, 1, 1))
    if isinstance(_end_date, date):
        end_date = _end_date.strftime("%Y-%m-%d")
    else:
        raise ValueError()

    ids = st.sidebar.multiselect(
        "Select funds",
        options=available_funds,
        default=OPTIMISATION_IDS,
        max_selections=30,
    )

    # Returns & risk models for funds
    fund_profiles = pd.DataFrame(get_expected_returns(start_date, end_date, ids))
    risk_model = pd.DataFrame(get_risk_model(start_date, end_date, ids))
    fund_profiles["implied_standard_deviation"] = np.sqrt(np.diag(risk_model.drop(columns="id").to_numpy()))

    # Generate and format efficient frontier
    _frontier_result = get_efficient_fronter(start_date, end_date, ids, n_portfolios)
    risk_return = pd.DataFrame(
        [
            {
                "expected_return": portfolio["expected_return"],
                "implied_standard_deviation": portfolio["implied_standard_deviation"],
            }
            for portfolio in _frontier_result
        ]
    )
    weights = pd.concat(
        [
            pd.json_normalize(portfolio["portfolio"]).set_index("id").transpose()
            for portfolio in _frontier_result
        ]
    ).reset_index(drop=True)
    frontier_result = pd.concat([risk_return, weights], axis=1)

    # Plot frontier
    frontier_chart = ef_scatter_plot(frontier_result)

    # Main page
    st.title("Portfolio Optimisation")
    if st.checkbox("Include individual funds"):
        individual_scatter = scatter_plot(fund_profiles)
        frontier_chart = frontier_chart + individual_scatter
    st.altair_chart(frontier_chart, use_container_width=True)  # type: ignore

    with st.expander("Assumptions"):
        # Apply pandas styling
        fund_profiles = fund_profiles.style.format(
            dict.fromkeys(["expected_return", "implied_standard_deviation"], "{:,.2%}".format)
        )
        st.write(fund_profiles)


main()
