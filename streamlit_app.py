import streamlit as st

st.set_page_config(page_title="Portfolio Builder", page_icon="📊", layout="wide")

screener = st.Page("dashboard/screener.py", title="Screener", icon=":material/search:", default=True)
backtest = st.Page("dashboard/backtest.py", title="Backtest", icon=":material/monitoring:")
optimisation = st.Page("dashboard/optimisation.py", title="Optimisation", icon=":material/analytics:")

pg = st.navigation(
    {
        "Portfolio Builder": [screener, backtest, optimisation],
    }
)

if __name__ == "__main__":
    pg.run()
