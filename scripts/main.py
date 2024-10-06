import polars as pl

from scripts.vanguard import Vanguard

vg_funds = [
    "vanguard-us-equity-index-fund-gbp-acc",
    "vanguard-uk-inflation-linked-gilt-index-fund-gbp-acc",
    "vanguard-ftse-uk-all-share-index-unit-trust-gbp-acc",
    "vanguard-ftse-100-index-unit-trust-gbp-acc",
    "vanguard-ftse-uk-equity-income-index-fund-gbp-acc",
    "vanguard-ftse-developed-europe-ex-uk-equity-index-fund-gbp-acc",
    "vanguard-ftse-developed-world-ex-uk-equity-index-fund-gbp-acc",
    "vanguard-ftse-global-all-cap-index-fund-gbp-acc",
    "vanguard-uk-long-duration-gilt-index-fund-gbp-acc",
    "vanguard-emerging-markets-stock-index-fund-gbp-acc",
    "vanguard-euro-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-euro-investment-grade-bond-index-fund-gbp-hedged-acc",
    "vanguard-japan-government-bond-index-fund-gbp-hedged-acc",
    "vanguard-japan-stock-index-fund-gbp-acc",
    "vanguard-pacific-ex-japan-stock-index-fund-gbp-acc",
    "vanguard-uk-government-bond-index-fund-gbp-acc",
    "vanguard-uk-investment-grade-bond-index-fund-gbp-acc",
    "vanguard-us-investment-grade-credit-index-fund-gbp-hedged-acc",
    "vanguard-us-government-bond-index-fund-gbp-hedged-acc",
]


def main() -> None:
    """Download fund data for all managers."""
    fund_details = []
    fund_returns = []
    mapping = {Vanguard(): vg_funds}

    for manager, funds in mapping.items():
        _details, _returns = manager.download_all(funds)
        fund_details.append(_details)
        fund_returns.append(_returns)

    pl.concat(fund_details).write_parquet("data/fund_details.pq")
    pl.concat(fund_returns).write_parquet("data/fund_returns.pq")


if __name__ == "__main__":
    main()
