class Config:
    def colors(self):
        return {
            "first": "#ED254E",
            "second": "#1E2019",
            "third": "#361D2E",
            "fourth": "#3C6997",
            "fifth": "#EEE2DF",
        }

    def format_pct(self):
        return {
            "CAGR": "{:.2%}",
            "Monthly standard deviation": "{:.2%}",
            "Maximum drawdown": "{:.2%}",
            "Monthly arithmetic mean": "{:.2%}",
            "Annual arithmetic mean": "{:.2%}",
            "Monthly geomtric mean": "{:.2%}",
            "Annual geomtric mean": "{:.2%}",
            "Monthly downside standard deviation": "{:.2%}",
            "R squared": "{:.2%}",
        }

    def format_dec(self):
        return {
            "Alpha": "{:.2f}",
            "Beta": "{:.2f}",
            "Sharpe ratio": "{:.2f}",
            "Sortino ratio": "{:.2f}",
            "Market correlation": "{:.2f}",
            "Treynor ratio": "{:.2f}",
            "Calmar ratio": "{:.2f}",
            "Active return": "{:.2f}",
            "Tracking error": "{:.2f}",
            "Information ratio": "{:.2f}",
            "Upside capture ratio": "{:.2f}",
            "Downside capture ratio": "{:.2f}",
            "Capture ratio": "{:.2f}",
        }

    def column_map(self):
        return {
            "cagr": "CAGR",
            "std_m": "Monthly standard deviation",
            "max_drawdown": "Maximum drawdown",
            "sharpe_ratio": "Sharpe ratio",
            "sortino_ratio": "Sortino ratio",
            "market_correlation": "Market correlation",
            "arithmetic_mean_m": "Monthly arithmetic mean",
            "arithmetic_mean_y": "Annual arithmetic mean",
            "geometric_mean_m": "Monthly geomtric mean",
            "geometric_mean_y": "Annual geomtric mean",
            "std_m": "Monthly standard deviation",
            "std_downside_m": "Monthly downside standard deviation",
            "alpha": "Alpha",
            "beta": "Beta",
            "r_squared": "R squared",
            "cagr": "CAGR",
            "treynor_ratio": "Treynor ratio",
            "calmar_ratio": "Calmar ratio",
            "active_return": "Active return",
            "tracking_error": "Tracking error",
            "information_ratio": "Information ratio",
            "upside_capture_ratio": "Upside capture ratio",
            "downside_capture_ratio": "Downside capture ratio",
            "capture_ratio": "Capture ratio",
            "returns": "Monthly arithmetic mean",
            "std": "Monthly standard deviation",
            "Intercept": "Alpha (bps)",
            "coefficient": "Coefficients",
            "standard_errors": "Standard errors",
            "pvalues": "P values",
            "conf_lower": "Lower Confidence Level",
            "conf_higher": "Higher Confidence Level",
        }
