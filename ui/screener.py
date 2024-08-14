from typing import Any

import httpx
import pandas as pd
import streamlit as st

from ui.config import settings


@st.cache_data(ttl="7d")
def get_funds() -> Any:
    """Get funds."""
    r = httpx.get(f"{settings.base_url}funds/all/", timeout=settings.timeout)
    return r.json()


def main() -> None:
    """Screener page."""
    df = pd.DataFrame(get_funds())
    df = df.drop(columns=["id"])
    return_cols = df.columns[df.columns.str.contains("returns")].tolist()
    df = df.style.format({i: "{:,.2%}".format for i in return_cols})

    st.title("Fund Screener")
    st.dataframe(df)


main()
