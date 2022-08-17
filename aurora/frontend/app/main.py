import streamlit as st
from modules.backtest import Backtest
from modules.factor import display_factor
from modules.optimisation import display_optimisation

st.set_page_config(layout="wide")

st.sidebar.title("Aurora")

options = {
    "Portfolio backtesting": Backtest().display,
    "Factor regression": display_factor,
    "Portfolio optimisation": display_optimisation,
}

page = st.sidebar.selectbox("Page Navigation", options)

options[page]()
