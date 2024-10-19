from abc import ABC, abstractmethod
from datetime import date

import polars as pl


class Manager(ABC):
    """Base manager class."""

    min_inception_date: date

    @abstractmethod
    def download_all(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Download all funds."""
        ...
