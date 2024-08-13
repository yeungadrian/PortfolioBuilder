from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Settings for streamlit dashboard."""

    model_config = SettingsConfigDict(env_prefix="api_")
    timeout: float = 30
    base_url: str = "http://localhost:8000/"


settings = APISettings()
