from datetime import date

import polars as pl

from scripts.vanguard import Vanguard

MIN_INCEPTION_DATE = date(2015, 1, 1)


def main() -> None:
    """Download fund data for all managers."""
    security_details = []
    security_returns = []
    managers = [Vanguard]

    for manager in managers:
        _details, _returns = manager(min_inception_date=MIN_INCEPTION_DATE).download_all()
        security_details.append(_details)
        security_returns.append(_returns)

    pl.concat(security_details).write_parquet("data/security_details.pq")
    pl.concat(security_returns).write_parquet("data/security_returns.pq")


if __name__ == "__main__":
    main()
