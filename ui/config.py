from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Settings for streamlit dashboard."""

    model_config = SettingsConfigDict(env_prefix="api_")
    timeout: float = 30
    base_url: HttpUrl = "http://localhost:8000"
    funds_path: str = "/funds/all"
    backtest_path: str = "/backtest"


settings = APISettings()
