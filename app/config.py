"""Settings for app."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for application."""

    title: str = "PortfolioBuilder"
    version: str = "1.0.0"
    security_details: Path = Path("sample/security_details.pq")
    security_returns: Path = Path("sample/security_returns.pq")


settings = Settings()
