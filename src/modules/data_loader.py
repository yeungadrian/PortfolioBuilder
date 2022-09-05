import requests
import streamlit as st

host = st.secrets["AURORA_URL"]

urls = {
    "funds": f"{host}/funds/",
    "backtest": f"{host}/backtest/",
    "factor": f"{host}/factor_analysis/",
    "factor_rolling": f"{host}/factor_analysis/rolling",
    "optimisation": f"{host}/optimisation/",
}


class DataLoader:
    @st.cache()
    def get_funds(self):
        url_funds = urls["funds"]
        response = requests.get(url_funds).json()

        return response

    @st.cache()
    def backtest(self, json_input):
        url_backtest = urls["backtest"]
        response = requests.post(url=url_backtest, json=json_input).json()

        return response

    @st.cache()
    def factor_regression(self, json_input):
        url_factor = urls["factor"]
        response = requests.post(url=url_factor, json=json_input).json()

        return response

    @st.cache()
    def rolling_factor_regression(self, json_input):
        url_factor = urls["factor_rolling"]
        response = requests.post(url=url_factor, json=json_input).json()

        return response

    @st.cache()
    def efficient_frontier(self, json_input):
        url_optimisation = urls["optimisation"]
        response = requests.post(url=url_optimisation, json=json_input).json()

        return response
