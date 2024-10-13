from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Settings for streamlit dashboard."""

    model_config = SettingsConfigDict(env_prefix="API_")
    timeout: float = 30
    base_url: HttpUrl = "http://localhost:8000"
    securities_path: str = "/securities/all/"
    backtest_path: str = "/backtest/"
    expected_return_path: str = "/optimisation/expected-returns/"
    risk_model_path: str = "/optimisation/risk-model?method=sample_cov"
    efficient_fronter_path: str = "/optimisation/efficient-frontier/"
    color_primary: str = "teal"
    color_scale: str = "teals"


settings = APISettings()
