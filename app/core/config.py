from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Paths for data."""

    security_details: str = "data/security_details.pq"
    security_returns: str = "data/security_returns.pq"


data_settings = DataSettings()
