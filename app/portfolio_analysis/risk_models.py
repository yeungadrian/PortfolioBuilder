"""Module for calculating risk models."""

import numpy as np
from sklearn.covariance import ledoit_wolf


def get_sample_covariance(security_returns: np.ndarray, frequency: int = 12) -> np.ndarray:
    """Calculate risk model based on sample covariance.

    Parameters
    ----------
    security_returns : np.ndarray
        returns for security
    frequency : int, optional
        number of points per year (252 - daily, 12 - monthly, 1 - yearly), by default 12

    Returns
    -------
    np.ndarray
        sample covariance
    """
    sample_covariance = np.cov(
        security_returns,
        rowvar=False,
    )
    return sample_covariance * frequency


def get_leodit_wolf_covariance(security_returns: np.ndarray) -> np.ndarray:
    """Calculate Ledoit-Wolf shrinkage estimate for a particular shrinkage target.

    Parameters
    ----------
    security_returns : np.ndarray
        returns for securities

    Returns
    -------
    np.ndarray
        Ledoit-Wolf shrinkage estimate
    """
    shrunk_cov, _ = ledoit_wolf(security_returns)
    return shrunk_cov
