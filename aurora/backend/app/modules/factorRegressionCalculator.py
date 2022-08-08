import pandas as pd
import statsmodels.formula.api as smf
import json
import numpy as np


def calculate_factor_regression(
    fund_code,
    regression_factors,
    historical_returns,
    frenchfama_Factors,
):

    np.random.seed(1000)

    regression_equation = " + ".join(regression_factors)

    historical_returns = historical_returns.set_index("date")
    historical_returns.index.name = None

    frenchfama_Factors = frenchfama_Factors.set_index("date")
    frenchfama_Factors.index.name = None

    regression_data = pd.concat(
        [historical_returns, frenchfama_Factors], axis=1, join="inner"
    )

    regression_data[fund_code] = regression_data[fund_code] - regression_data["RF"]

    model = smf.ols(
        formula=f"{fund_code} ~ {regression_equation}", data=regression_data
    )

    results = model.fit()

    output = get_summary_results(results, fund_code)

    return output


def get_summary_results(results, fund_code):
    """take the result of an statsmodel results table and transforms it into a dataframe
    https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.html"""
    pvals = results.pvalues
    coefficient = results.params
    conf_lower = results.conf_int()[0]
    conf_higher = results.conf_int()[1]
    standard_errors = results.bse
    residuals = results.resid
    num_obs = results.nobs
    rsquared = results.rsquared
    rsquard_adj = results.rsquared_adj
    fvalue = results.fvalue

    output_result = {
        "fundCode": fund_code,
        "numberObservations": num_obs,
        "rSquared": rsquared,
        "rSquaredAdjusted": rsquard_adj,
        "fValue": fvalue,
        "coefficient": coefficient,
        "standardErrors": standard_errors,
        "pValues": pvals,
        "confidenceIntervalLower": conf_lower,
        "confidenceIntervalHigher": conf_higher,
        "residuals": residuals,
    }

    return output_result
