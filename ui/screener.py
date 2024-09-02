from typing import Any

import pandas as pd
import requests
import streamlit as st

from ui.config import settings


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get available funds."""
    r = requests.get(f"{settings.base_url}{settings.funds_path}", timeout=settings.timeout)
    return r.json()


def main() -> None:
    """Screener page."""
    # Get and format fund data
    df = pd.DataFrame(get_funds())
    df = df.drop(columns=["id"])
    return_cols = df.columns[df.columns.str.contains("returns")].tolist()
    df = df.style.format({i: "{:,.2%}".format for i in return_cols})

    # Main page
    st.title("Fund Screener")
    st.dataframe(df)


main()
