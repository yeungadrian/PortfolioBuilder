"""Module for calculating portfolio metrics."""

from datetime import date

import numpy as np
import polars as pl

from app.models import PortfolioMetrics


def _diff_in_months(start_date: date, end_date: date) -> int:
    """Calculate difference of two dates in months, order matters.

    Parameters
    ----------
    start_date : date
        first date
    end_date : date
        second date

    Returns
    -------
    int
        Difference in months
    """
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def get_portfolio_return(start_value: float, end_value: float) -> float:
    """Calculate portfolio return.

    Parameters
    ----------
    start_value : float
        initial value
    end_value : float
        final value

    Returns
    -------
    float
        portfolio return
    """
    return (end_value / start_value) - 1


def get_cagr(start_value: float, end_value: float, start_date: date, end_date: date) -> float:
    """Calculate compound annnual growth rate.

    CAGR = ((Final Value/Initial Value)^(1/N) - 1)

    Parameters
    ----------
    start_value : float
        initial value
    end_value : float
        final value
    start_date : date
        start date
    end_date : date
        end date

    Returns
    -------
    float
        cagr
    """
    n_years = _diff_in_months(start_date, end_date) / 12
    return float(((end_value / start_value) ** (1 / n_years)) - 1)


def get_max_drawdown(portfolio_values: pl.DataFrame) -> float:
    """Calculate max drawdown.

    MDD = (Trough Value - Peak Value) / Peak Value

    Parameters
    ----------
    portfolio_values : pl.DataFrame
        Portfolio value over time.

    Returns
    -------
    float
        Max drawdown
    """
    portfolio_values = portfolio_values.with_columns(
        pl.col("portfolio_value")
        .rolling_max(window_size=portfolio_values.shape[0], min_samples=1)
        .alias("portfolio_max")
    ).with_columns(
        ((pl.col("portfolio_max") - pl.col("portfolio_value")) / pl.col("portfolio_max")).alias("drawdown")
    )
    return float(portfolio_values["drawdown"].max())  # type: ignore


def get_portfolio_std(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Estimate portfolio standard deviation using covariance.

    Parameters
    ----------
    weights : np.ndarray
        portfolio weights
    covariance : np.ndarray
        covariance matrix / risk model

    Returns
    -------
    float
        portfolio standard deviation
    """
    weights = np.array(weights)
    std = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
    return float(std)


def get_portfolio_metrics(
    portfolio_values: pl.DataFrame, start_date: date, end_date: date
) -> PortfolioMetrics:
    """Calculate common portfolio metrics.

    Parameters
    ----------
    portfolio_values : pl.DataFrame
        Portfolio values over time in dataframe.
    start_date : date
        start date
    end_date : date
        end date

    Returns
    -------
    PortfolioMetrics
        Common portfolio metrics
    """
    portfolio_values = portfolio_values.with_columns(
        (pl.col("portfolio_value") / pl.col("portfolio_value").shift() - 1).alias("portfolio_return")
    )
    start_value = portfolio_values["portfolio_value"].head(1)[0]
    end_value = portfolio_values["portfolio_value"].tail(1)[0]

    return PortfolioMetrics(
        portfolio_return=get_portfolio_return(start_value, end_value),
        cagr=get_cagr(start_value, end_value, start_date, end_date),
        standard_deviation=portfolio_values["portfolio_return"].std(),  # type: ignore
        max_drawdown=get_max_drawdown(portfolio_values.select("portfolio_value")),
    )
