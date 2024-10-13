import streamlit as st

st.set_page_config(page_title="Portfolio Builder", page_icon="📊", layout="wide")

backtest = st.Page("backtest.py", title="Backtest", icon=":material/monitoring:", default=True)
optimisation = st.Page("optimisation.py", title="Optimisation", icon=":material/analytics:")

pg = st.navigation(
    {
        "Portfolio Builder": [backtest, optimisation],
    }
)

if __name__ == "__main__":
    pg.run()
