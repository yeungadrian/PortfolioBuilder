import httpx
import pandas as pd
import streamlit as st

BASE_URL = "http://localhost:8000/"


st.set_page_config(page_title="Ex-stream-ly Cool App", page_icon="🧊", layout="wide")


def screener_page() -> None:
    """Screener page."""
    r = httpx.get(f"{BASE_URL}funds/all/")
    df = pd.DataFrame(r.json())
    return_cols = df.columns[df.columns.str.contains("returns")].tolist()
    df = df.style.format({i: "{:,.2%}".format for i in return_cols})

    st.title("Fund Screener")
    st.dataframe(df)


def main() -> None:
    """Streamlit dashboard."""
    page_index = st.sidebar.radio("Navigation", ["Screener", "Backtest", "Optimisation"])

    match page_index:
        case "Screener":
            screener_page()


if __name__ == "__main__":
    main()
