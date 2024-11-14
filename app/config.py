from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for application."""

    security_details: Path = Path("sample/security_details.pq")
    security_returns: Path = Path("sample/security_returns.pq")


settings = Settings()
