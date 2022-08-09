import streamlit as st
from modules.backtest import display_backtest
from modules.factor import display_factor
from modules.optimisation import display_optimisation

st.sidebar.title("Aurora")

options = {
    "Portfolio backtesting": display_backtest,
    "Factor regression": display_factor,
    "Portfolio optimisation": display_optimisation,
}


page = st.sidebar.selectbox("Page Navigation", options)

options[page]()
