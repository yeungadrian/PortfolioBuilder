"""Settings for app."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for application."""

    title: str = "PortfolioBuilder"
    version: str = "1.0.0"
    security_details: str = "sample/security_details.pq"
    security_returns: str = "sample/security_returns.pq"


settings = Settings()
