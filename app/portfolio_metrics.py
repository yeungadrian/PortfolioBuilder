"""Functions to calculate metrics for a give portfolio."""

from datetime import date

import numpy as np
import polars as pl


def _diff_in_months(date1: date, date2: date) -> int:
    """Calculate difference of two dates in months."""
    return (date2.year - date1.year) * 12 + (date2.month - date1.month)


def calculate_portfolio_return(start_value: float, end_value: float) -> float:
    """Calculate portfolio return."""
    return (end_value / start_value) - 1


def calculate_cagr(start_value: float, end_value: float, start_date: date, end_date: date) -> float:
    """Compound annnual growth rate."""
    n_years = _diff_in_months(start_date, end_date) / 12
    return float(((end_value / start_value) ** (1 / n_years)) - 1)


def calculate_max_drawdown(security_returns: pl.DataFrame) -> float:
    """Calculate max drawdown."""
    security_returns = security_returns.with_columns(
        pl.col("portfolio_value")
        .rolling_max(window_size=security_returns.shape[0], min_periods=1)
        .alias("portfolio_max")
    ).with_columns(
        ((pl.col("portfolio_max") - pl.col("portfolio_value")) / pl.col("portfolio_max")).alias("drawdown")
    )
    return float(security_returns["drawdown"].max())


def calculate_portfolio_std(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Calculate portfolio standard deviation using covariance."""
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
    return float(std)
