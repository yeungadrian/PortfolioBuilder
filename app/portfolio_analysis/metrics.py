"""Functions to get metrics for a give portfolio."""

from datetime import date

import numpy as np
import polars as pl

from app.models import PortfolioMetrics


def _diff_in_months(date1: date, date2: date) -> int:
    """Calculate difference of two dates in months."""
    return (date2.year - date1.year) * 12 + (date2.month - date1.month)


def get_portfolio_return(start_value: float, end_value: float) -> float:
    """Calculate portfolio return."""
    return (end_value / start_value) - 1


def get_cagr(start_value: float, end_value: float, start_date: date, end_date: date) -> float:
    """Compound annnual growth rate."""
    n_years = _diff_in_months(start_date, end_date) / 12
    return float(((end_value / start_value) ** (1 / n_years)) - 1)


def get_max_drawdown(portfolio_values: pl.DataFrame) -> float:
    """Calculate max drawdown."""
    portfolio_values = portfolio_values.with_columns(
        pl.col("portfolio_value")
        .rolling_max(window_size=portfolio_values.shape[0], min_periods=1)
        .alias("portfolio_max")
    ).with_columns(
        ((pl.col("portfolio_max") - pl.col("portfolio_value")) / pl.col("portfolio_max")).alias("drawdown")
    )
    return float(portfolio_values["drawdown"].max())


def get_portfolio_std(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Calculate portfolio standard deviation using covariance."""
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
    return float(std)


def get_portfolio_metrics(
    portfolio_values: pl.DataFrame, start_date: date, end_date: date
) -> PortfolioMetrics:
    """Calculate common portfolio metrics."""
    portfolio_values = portfolio_values.with_columns(
        (pl.col("portfolio_value") / pl.col("portfolio_value").shift() - 1).alias("portfolio_return")
    )
    start_value = portfolio_values["portfolio_value"].head(1)[0]
    end_value = portfolio_values["portfolio_value"].tail(1)[0]

    return PortfolioMetrics(
        portfolio_return=get_portfolio_return(start_value, end_value),
        cagr=get_cagr(start_value, end_value, start_date, end_date),
        standard_deviation=portfolio_values["portfolio_return"].std(),
        max_drawdown=get_max_drawdown(portfolio_values.select("portfolio_value")),
    )
