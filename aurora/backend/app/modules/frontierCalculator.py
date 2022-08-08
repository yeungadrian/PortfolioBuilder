import pandas as pd
import json
import numpy as np
from scipy.optimize import minimize


def portfolio_return(weights, fund_returns):
    annualised_return = np.sum(fund_returns * weights)

    return annualised_return


def portfolio_std(weights, fund_returns, fund_covariance):
    std = np.sqrt(np.dot(weights, np.dot(fund_covariance, weights)))
    return std


def efficient_return(fund_returns, fund_covariance, target):
    args = (fund_returns, fund_covariance)
    num_funds = len(fund_returns)

    def portfolio_return(weights):
        annualised_return = np.sum(fund_returns * weights)

        return annualised_return

    constraints = (
        {"type": "eq", "fun": lambda x: portfolio_return(x) - target},
        {"type": "eq", "fun": lambda x: np.sum(x) - 1},
    )
    bounds = tuple((0, 1) for asset in range(num_funds))
    initial_weights = num_funds * [
        1.0 / num_funds,
    ]
    result = minimize(
        portfolio_std,
        initial_weights,
        args=args,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    ).x
    result = [round(elem, 6) for elem in result]
    return result


def calculate_efficient_frontier(fund_returns, fund_covariance, portfolios):
    return_range = (fund_returns.max() - fund_returns.min()) / (portfolios - 1)
    efficient_range = []
    for i in range(portfolios):
        efficient_range.append(fund_returns.min() + return_range * i)

    efficient_portfolios = []

    for j in efficient_range:
        efficient_portfolios.append(efficient_return(fund_returns, fund_covariance, j))

    return efficient_portfolios


def efficient_frontier_metrics(fund_returns, fund_covariance, portfolios, fund_codes):

    efficient_portfolios = calculate_efficient_frontier(
        fund_returns, fund_covariance, portfolios
    )

    result = []
    for i in efficient_portfolios:
        portfolio_weights = {}
        for j in range(len(fund_codes)):
            portfolio_weights[fund_codes[j]] = i[j]
        result.append(
            {
                "portfolioWeights": portfolio_weights,
                "returns": round(portfolio_return(i, fund_returns), 6),
                "std": round(portfolio_std(i, fund_returns, fund_covariance), 6),
            }
        )

    return result
