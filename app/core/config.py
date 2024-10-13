from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Paths for data."""

    fund_details: str = "data/fund_details.pq"
    fund_returns: str = "data/fund_returns.pq"


data_settings = DataSettings()
