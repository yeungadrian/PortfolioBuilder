from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Paths for data."""

    security_details: str = "sample/security_details.pq"
    security_returns: str = "sample/security_returns.pq"


data_settings = DataSettings()
