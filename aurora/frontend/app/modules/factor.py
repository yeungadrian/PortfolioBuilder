from datetime import datetime

import altair as alt
import pandas as pd
import requests
import streamlit as st
from modules.funds import factorRegression, get_funds

config = {
    "Intercept": "Alpha (bps)",
    "coefficient": "Coefficients",
    "standard_errors": "Standard errors",
    "pvalues": "P values",
    "conf_lower": "Lower Confidence Level",
    "conf_higher": "Higher Confidence Level",
}


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

    def ticker_details(self, regression, regression_input):

        for ticker in regression:

            start_date = regression_input["start_date"]
            end_date = regression_input["end_date"]
            time_period = f"{start_date} to {end_date}"
            num_obs = round(ticker["num_observations"], 0)
            r_squared = round(ticker["rsquared"] * 100.0, 2)
            adj_r_squared = round(ticker["rsquared_adj"] * 100.0, 2)
            f_value = round(ticker["fvalue"], 3)

            dw_stats = round(ticker["durbin_watson"], 4)
            autocorrelation = "No Auto correlation detected"
            if (dw_stats < 1.5) or (dw_stats > 2.5):
                autocorrelation = "Auto correlation detected"

            bp_stats = round(ticker["breusch_pagan"]["lm_pvalue"], 4)
            heteroscedasticity = "No heteroscedasticity detected"
            if bp_stats > 0.05:
                heteroscedasticity = "Heteroscedasticity detected"

            regression_stats = pd.DataFrame(
                {
                    "Time Period": time_period,
                    "Regression Basis": f"{num_obs} periods",
                    "R squared": f"{r_squared} %",
                    "Adjusted R squared": f"{adj_r_squared} %",
                    "Regression F statistic": f_value,
                    "Autocorrelation": f"{autocorrelation} , Durbin watson statistic of {dw_stats}",
                    "Heteroscedasticity": f"{heteroscedasticity}, Breusch Pagan P value of {bp_stats}",
                },
                index=[ticker["fund_code"]],
            ).transpose()

            keys = [
                "coefficient",
                "standard_errors",
                "pvalues",
                "conf_lower",
                "conf_higher",
            ]
            details = [ticker.get(key) for key in keys]

            details = pd.DataFrame(details).rename(columns=config)

            details = details.transpose()

            details.columns = keys

            details.loc[
                details.index == "Alpha (bps)", ~details.columns.isin(["pvalues"])
            ] = (
                details.loc[
                    details.index == "Alpha (bps)", ~details.columns.isin(["pvalues"])
                ]
                * 10000
            )

            details = details.rename(columns=config)

            with st.expander(ticker["fund_code"]):

                st.dataframe(regression_stats)

                st.dataframe(details.style.format("{:.2f}"))

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

    def rolling_regression(self, regression_inputs):

        data = requests.post(
            "http://localhost:8000/factor_analysis/rolling/", json=regression_inputs
        ).json()

        with st.expander("Rolling regression"):

            for ticker in data:

                rolling_results = pd.DataFrame(ticker["params"]).reset_index()
                rolling_results = rolling_results.rename(
                    columns={"index": "Date", "Intercept": "Alpha"}
                )
                rolling_results = rolling_results[
                    regression_inputs["factors"] + ["Date"]
                ]
                rolling_results = pd.melt(
                    rolling_results,
                    id_vars="Date",
                    value_name="Coefficients",
                    var_name="Factor",
                )

                rolling_chart = (
                    alt.Chart(rolling_results)
                    .mark_line()
                    .encode(
                        x="Date:T",
                        y="Coefficients",
                        color="Factor",
                        tooltip=["Date", "Coefficients", "Factor"],
                    )
                )
                st.subheader(ticker["fund_code"])
                st.altair_chart(rolling_chart, use_container_width=True)

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

            self.ticker_details(regression_response, regression_input)

            self.residuals(regression_response)

            self.rolling_regression(regression_input)
