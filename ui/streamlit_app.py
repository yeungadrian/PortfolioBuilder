import streamlit as st

st.set_page_config(page_title="Portfolio Builder", page_icon="📊", layout="wide")

screener = st.Page("ui/screener.py", title="Screener", icon=":material/search:", default=True)
backtest = st.Page("ui/backtest.py", title="Backtest", icon=":material/monitoring:")
optimisation = st.Page("ui/optimisation.py", title="Optimisation", icon=":material/analytics:")

pg = st.navigation(
    {
        "Portfolio Builder": [screener, backtest, optimisation],
    }
)

if __name__ == "__main__":
    pg.run()
