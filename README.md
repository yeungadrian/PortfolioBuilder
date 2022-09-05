# Portfolio Builder
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://yeungadrian-portfoliobuilder-srcmain-wdkrcb.streamlitapp.com/)

Portfolio analytics tools to help compare portfolios deployed on streamlit cloud

## Financial Analysis:
- Portfolio Backtesting
    - Backtest different asset allocations and compare historical performance
- Factor Analysis
    - Run regression analysis using French-Fama / other factor models
- Portfolio Optimisation
    - Generate efficient frontiers to explore risk return trade offs

![](image/backtest.png)
![](image/optimisation.png)

## Run locally:

### Requirements:
API needs to be setup from https://github.com/yeungadrian/PortfolioBuilderAPI

Get started locally by creating a virtual environment via conda or venv and running:
```
pip install -r requirements.txt
streamlit run src/main.py
```