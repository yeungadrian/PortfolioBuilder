import requests
import streamlit as st

urls = {
    "funds": "http://localhost:8000/funds/",
    "backtest": "http://localhost:8000/backtest/",
    "factor": "http://localhost:8000/factor_analysis/",
    "optimisation": "http://localhost:8000/portfolioOptimisation/",
}


@st.cache()
def get_funds():
    url_funds = "http://localhost:8000/funds/"
    response = requests.get(url_funds).json()

    return response


@st.cache()
def backtest(json_input):
    url_backtest = "http://localhost:8000/backtest/"
    response = requests.post(url=url_backtest, json=json_input).json()

    return response


@st.cache()
def factorRegression(json_input):
    url_factor = "http://localhost:8000/factor_analysis/"
    response = requests.post(url=url_factor, json=json_input).json()

    return response


@st.cache()
def efficientFrontier(json_input):
    url_optimisation = "http://localhost:8000/portfolioOptimisation/"
    response = requests.post(url=url_optimisation, json=json_input).json()

    return response
