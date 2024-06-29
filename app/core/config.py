from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Paths for data."""

    fund_details: str = "data/processed/fund_details.pq"
    fund_returns: str = "data/processed/fund_returns.pq"


data_settings = DataSettings()
