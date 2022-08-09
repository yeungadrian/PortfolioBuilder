from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from modules.funds import factorRegression, get_funds


def display_factor():

    # Portfolio Backtesting

    st.title("Factor Regression")
    fund_list = pd.DataFrame(get_funds())

    st.sidebar.subheader("Regression inputs")

    start_date = st.sidebar.date_input(
        "Start Date", value=datetime(2017, 12, 31)
    ).strftime("%Y-%m-%d")
    end_date = st.sidebar.date_input("End Date", value=datetime(2020, 12, 31)).strftime(
        "%Y-%m-%d"
    )

    selected_funds = st.sidebar.multiselect(
        label="Fund selection",
        options=list(fund_list["Company"]),
        default=["Apple Inc."],
    )

    regression_factors = ["MktRF", "SMB", "HML", "RMW", "CMA"]

    selected_factors = st.sidebar.multiselect(
        label="Factor selection",
        options=regression_factors,
        default=["MktRF", "SMB", "HML"],
    )

    frequency = st.sidebar.selectbox(
        label="Return frequency",
        options=["Daily", "Monthly"],
    )

    selected_fund_list = []

    for i in range(0, len(selected_funds)):
        selected_fund_list.append(
            fund_list[fund_list["Company"] == selected_funds[i]]["Code"].reset_index(
                drop=True
            )[0]
        )

    submit = st.sidebar.button(label="Run")

    if submit:

        regression_input = {
            "startDate": start_date,
            "endDate": end_date,
            "funds": selected_fund_list,
            "regressionFactors": selected_factors,
            "frequency": frequency,
        }

        regression_response = factorRegression(regression_input)

        for i in regression_response:

            company = fund_list[fund_list["Code"] == i["fundCode"]][
                "Company"
            ].reset_index(drop=True)[0]
            regression_residuals = (
                pd.DataFrame(i["residuals"], index=[0]).transpose().reset_index()
            )

            metrics = [
                "coefficient",
                "standardErrors",
                "pValues",
                "confidenceIntervalLower",
                "confidenceIntervalHigher",
            ]

            metrics_json = {j: i[j] for j in metrics if j in i}

            st.markdown(
                f"""
                ## {company}
                """
            )

            st.table(
                pd.DataFrame(
                    {
                        "observations": i["numberObservations"],
                        "R Squared": round(i["rSquared"], 4),
                        "Adjusted R Squared": round(i["rSquaredAdjusted"], 4),
                    },
                    index=[0],
                )
            )

            alpha = round(i["coefficient"]["Intercept"] / 0.0001, 2)

            if frequency == "Monthly":
                annual_alpha = alpha * 12
            else:
                annual_alpha = round(alpha / 100 * 255, 2)

            st.markdown(
                f"""
            Alpha: {alpha}bps

            Annualised Alpha:  {annual_alpha}%
            """
            )

            dynamic_metrics = pd.DataFrame(metrics_json)
            dynamic_metrics.columns = [
                "cofficient",
                "standard error",
                "p-value",
                "95% lower",
                "95% higher",
            ]

            st.table(dynamic_metrics)

            regression_residuals.columns = ["date", "residual"]
            regression_residuals["date"] = pd.to_datetime(regression_residuals["date"])

            residual_chart = (
                alt.Chart(regression_residuals)
                .mark_circle()
                .encode(x="date", y="residual")
                .properties(width=700)
            )

            st.write(residual_chart)

            st.markdown(
                """
                ---
                """
            )
