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

Investment analytics app (FastAPI, Artifact Registry, Cloud Run)


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

## CI / CD
- Linting & Tests: Pre-commit + Pytests
- Build: Github Actions + Docker + Artifact Registry
- Deploy: Github actions + gcloud cli


## Inspiration
- [Folder structure: FastAPI full stack template](https://github.com/tiangolo/full-stack-fastapi-template)
- [Ruff config: polars](https://github.com/pola-rs/polars/blob/main/py-polars/pyproject.toml)
- [Github actions: FastAPI](https://github.com/tiangolo/fastapi/blob/master/.github/workflows/test.yml)
- [Google cloud free tier limits](https://cloud.google.com/free/docs/free-cloud-features#free-tier-usage-limits)


## Managing GCP costs
- Delete image before uploading new one (Each image is ~330MB so not small) (Switch to a cleanup policy, if some history matters to you)
- Log retention policy
- Set appropriate resource limits: CPU, MEMORY, MIN_INSTANCES, MAX_INSTANCES. App when idle uses 5% of CPU, ~128Mi memory.


## How to productionise
- Migrate data to a proper source (s3 / cloud storage / postgresql equivalent) (it's only 25KB atm)
- Cloud run by default has no pbulic access. (No dangerous operations, limits set way below cloud run free tier)
- Turn on image scanning in wherever you host your images
