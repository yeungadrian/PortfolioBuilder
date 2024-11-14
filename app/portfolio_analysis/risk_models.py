import numpy as np
from sklearn.covariance import ledoit_wolf


def get_sample_covariance(security_returns: np.ndarray, frequency: int = 12) -> np.ndarray:
    """Calculate risk model based on sample covariance."""
    sample_covariance = np.cov(
        security_returns,
        rowvar=False,
    )
    return sample_covariance * frequency


def get_leodit_wolf_covariance(security_returns: np.ndarray) -> np.ndarray:
    """Calculate Ledoit-Wolf shrinkage estimate for a particular shrinkage target."""
    shrunk_cov, _ = ledoit_wolf(security_returns)
    return shrunk_cov
