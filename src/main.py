import streamlit as st

from modules.backtest import Backtest
from modules.factor import FactorAnalysis
from modules.optimisation import Optimisation

st.set_page_config(layout="wide")

st.sidebar.title("Aurora")

options = {
    "Portfolio backtesting": Backtest().display,
    "Portfolio optimisation": Optimisation().display,
    "Factor analysis": FactorAnalysis().display,
}

page = st.sidebar.selectbox("Page Navigation", options)

options[page]()
