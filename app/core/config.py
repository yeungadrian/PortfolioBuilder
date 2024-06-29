from pydantic_settings import BaseSettings


class DataSettings(BaseSettings):
    """Paths for data."""

    fund_details: str = "data/processed/fund_details.json"
    fund_returns: str = "data/processed/fund_returns.json"


data_settings = DataSettings()
