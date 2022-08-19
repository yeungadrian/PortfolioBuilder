from typing import List, TypeVar

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pydantic import BaseModel

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


class Portfolio(BaseModel):
    fund_codes: List[str]
    start_date: str
    end_date: str
    price_df: PandasDataFrame
    french_fama_df: PandasDataFrame

    """
    def prepare_data(self):
        self.price_df["date"] = pd.to_datetime(self.price_df["date"])
        self.price_df = self.price_df.sort_values(by="date").reset_index(drop=True)
        self.price_df = self.price_df.loc[
            (self.price_df.date >= self.start_date)
            & (self.price_df.date <= self.end_date)
        ].reset_index(drop=True)
        self.french_fama_df.date = pd.to_datetime(ff_factors.date, format="%Y-%m-%d")
        self.french_fama_df = self.french_fama_df.rename(columns={"MktRF": "Mkt"})
    """

    def calculate_returns(self):

        columns = ["date"] + self.fund_codes
        subset_data = self.price_df[columns]
        for i in self.fund_codes:
            subset_data[i] = (subset_data[i] / subset_data[i].shift()) - 1

        subset_data = subset_data.dropna()

        return subset_data

    def get_summary_results(self, results, fund_code):
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

    def calculate_factor_regression(
        self, fund_code, regression_factors, frenchfama_Factors, historical_returns
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

        output = self.get_summary_results(results, fund_code)

        return output

    def regress_funds(self):
        fund_returns = self.calculate_returns()
        output = []

        for i in self.fund_codes:
            output.append(
                self.calculate_factor_regression(
                    i, ["Mkt", "SMB", "HML", "RMW"], self.french_fama_df, fund_returns
                )
            )
        return output
