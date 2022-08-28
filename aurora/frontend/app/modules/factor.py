from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from modules.funds import factorRegression, get_funds


class FactorAnalysis:
    def sidebar(self, fund_list):

        start_date = st.date_input("Start Date", value=datetime(2017, 12, 31)).strftime(
            "%Y-%m-%d"
        )
        end_date = st.date_input("End Date", value=datetime(2020, 12, 31)).strftime(
            "%Y-%m-%d"
        )

        funds = st.multiselect(
            label="Fund selection",
            options=list(fund_list["Company"]),
            default=["Apple Inc."],
        )

        regression_factors = ["MktRF", "SMB", "HML", "RMW", "CMA"]

        selected_factors = st.multiselect(
            label="Factor selection",
            options=regression_factors,
            default=["MktRF", "SMB", "HML"],
        )

        frequency = st.selectbox(
            label="Return frequency",
            options=["Daily", "Monthly"],
        ).lower()

        fund_codes = []

        for i in range(len(funds)):
            fund_codes.append(
                fund_list[fund_list["Company"] == funds[i]]["Code"].values[0]
            )

        regression_input = {
            "start_date": start_date,
            "end_date": end_date,
            "funds": fund_codes,
            "factors": selected_factors,
            "frequency": frequency,
        }

        return regression_input

    def annual_alpha(self, regression_input, alpha):
        if regression_input["frequency"] == "monthly":
            annual_alpha = (1 + (alpha)) ** 12 - 1
        else:
            annual_alpha = (1 + (alpha)) ** 252 - 1

        return annual_alpha

    def summary_table(self, fund_list, regression_input, regression):

        columns = (
            ["Ticker", "Start Date", "End Date"]
            + regression_input["factors"]
            + ["Alpha (bps)", "Annual Alpha", "R squared"]
        )

        summary = {}

        for i in regression:
            fund_summary = [i["fund_code"]]
            fund_summary = fund_summary + [
                regression_input["start_date"],
                regression_input["end_date"],
            ]
            for j in regression_input["factors"]:
                fund_summary.append(i["coefficient"][j])

            alpha = i["coefficient"]["Intercept"]
            fund_summary.append(alpha / 0.0001)
            fund_summary.append(self.annual_alpha(regression_input, alpha))

            fund_summary.append(i["rsquared"])

            company = fund_list[fund_list["Code"] == i["fund_code"]]["Company"].values[
                0
            ]

            summary[company] = fund_summary

        summary = pd.DataFrame(summary).transpose()
        summary.columns = columns

        st.dataframe(summary)

    def residuals(self, regression):
        with st.expander("Residuals"):

            residuals = pd.DataFrame()

            for i in regression:
                residual = pd.DataFrame(i["residuals"], index=[i["fund_code"]])
                residuals = pd.concat([residuals, residual])

            residuals = (
                residuals.transpose().reset_index().rename(columns={"index": "Date"})
            )

            residuals = pd.melt(
                residuals, id_vars="Date", var_name="Ticker", value_name="Residual"
            )

            residual_chart = (
                alt.Chart(residuals)
                .mark_circle()
                .encode(
                    x="Date:T",
                    y="Residual",
                    color="Ticker",
                    tooltip=["Date:T", "Residual"],
                )
            )

            st.altair_chart(residual_chart, use_container_width=True)

    def display(self):

        fund_list = pd.DataFrame(get_funds())

        st.title("Factor Analysis")

        with st.form("my_form"):
            with st.sidebar:
                regression_input = self.sidebar(fund_list)

                submitted = st.form_submit_button("Submit")

        if submitted:

            regression_response = factorRegression(regression_input)

            self.summary_table(fund_list, regression_input, regression_response)

            self.residuals(regression_response)
