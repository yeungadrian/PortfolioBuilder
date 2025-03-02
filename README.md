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

![](assets/backtest.png)

View live API docs @ https://portfoliobuilder-jfv66mvjvq-ew.a.run.app/redoc

Goals:
1. Minimalish but still effective FastAPI + Github Action setup
2. Exploring severless with Google Cloud (Artifact Regsitry, Cloud Run)
3. Refresh knowledge on portfolio optimisation

## Quickstart
Run locally with uv
```
uv sync --all-extras
uv run uvicorn app.main:app --reload
uv run streamlit run streamlit_app.py
```
Run locally with docker
```
docker build -t portfoliobuilder .
docker run --rm -it -p 8000:8000/tcp portfoliobuilder:latest
```
## Architecture

```mermaid
architecture-beta
    group github(cloud)[Github]
    service github_action(cloud)[Github Actions] in github


    group google_cloud(cloud)[Google Cloud]
    service artifact_registry(cloud)[Artifact Registry] in google_cloud
    service cloud_run(cloud)[Google Cloud Run] in google_cloud

    group StreamlitCloud(cloud)[Streamlit Cloud]
    service Streamlit(cloud)[Streamlit] in StreamlitCloud

    github_action:R --> L:artifact_registry
    github_action:R --> L:cloud_run
    artifact_registry:T --> B:cloud_run

    cloud_run:R --> L:Streamlit
```
Note: Mermaid supported icons is very limited for now.
