import polars as pl

from app.loader import load_returns
from app.models import BacktestScenario


def run_backtesting(backtest_scenario: BacktestScenario) -> pl.DataFrame:
    """Run backtesting."""
    ids = [i.id for i in backtest_scenario.portfolio]
    security_returns = load_returns(ids, backtest_scenario.start_date, backtest_scenario.end_date)
    # Set return for day 0 to 0.
    security_returns = security_returns.with_columns(
        [
            pl.when(pl.col("date") == pl.col("date").min()).then(0).otherwise(pl.col(_id)).alias(_id)
            for _id in ids
        ]
    )
    # Calculate monthly returns
    security_returns = security_returns.with_columns(
        [(pl.col(_id) + 1.0).cum_prod().alias(_id) - 1.0 for _id in ids]
    )
    security_returns = security_returns.with_columns(
        [
            ((pl.col(holding.id) + 1.0) * holding.amount).alias(holding.id)
            for holding in backtest_scenario.portfolio
        ]
    )
    security_returns = security_returns.with_columns(pl.sum_horizontal(ids).alias("portfolio_value"))
    return security_returns
