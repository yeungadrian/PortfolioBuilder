# PortfolioBuilder

<p align="center">
<a href="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/test.yml?query=branch%3Amain+event%3Apush+" target="_blank">
    <img src="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/test.yml/badge.svg?branch=main&event=push" alt="Test">
</a>
<a href="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/build-push.yml?query=branch%3Amain" target="_blank">
    <img src="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/build-push.yml/badge.svg?branch=main" alt="Build">
</a>
<a href="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/deploy.yml?query=branch%3Amain" target="_blank">
    <img src="https://github.com/yeungadrian/PortfolioBuilder/actions/workflows/deploy.yml/badge.svg?branch=main" alt="Deploy">
</a>
</p>

Investment analytics (FastAPI, Artifact Registry, Cloud Run)

## Quickstart
Run locally with poetry
```
poetry shell
poetry install --with dev
uvicorn src.main:app --reload --port 8000
```
Run with docker
```
docker build -t portfoliobuilder . --build-arg="POETRY_VERSION=1.8.3"
docker run --rm -it -p 8000:8000/tcp portfoliobuilder:latest
```

## Inspiration
- [Folder structure: FastAPI full stack template](https://github.com/tiangolo/full-stack-fastapi-template)
- [Ruff config: polars](https://github.com/pola-rs/polars/blob/main/py-polars/pyproject.toml)
- [Github actions: FastAPI](https://github.com/tiangolo/fastapi/blob/master/.github/workflows/test.yml)
- [Google cloud free tier limits](https://cloud.google.com/free/docs/free-cloud-features#free-tier-usage-limits)
- [PyPortfolioOpt](https://pypi.org/project/pyportfolioopt/)
