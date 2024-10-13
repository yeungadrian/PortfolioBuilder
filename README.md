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

Goals:
1. Best practices for FastAPI + Github Actions
2. Exploring severless with Google Cloud (Artifact Regsitry, Cloud Run)
3. Refresh portfolio optimisation techniques

## Quickstart
Run locally with uv
```
uv sync --all-extras --dev
uv run -- uvicorn app.main:app --reload
uv run -- streamlit run streamlit_app.py
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
    service code(disk)[Code] in github
    service github_action(cloud)[Github Actions] in github
    service docker(cloud)[Docker] in github

    group google_cloud(cloud)[Google Cloud]
    service artifact_registry(cloud)[Artifact Registry] in google_cloud
    service cloud_run(cloud)[Google Cloud Run] in google_cloud

    group StreamlitCloud(cloud)[Streamlit Cloud]
    service Streamlit(cloud)[Streamlit] in StreamlitCloud

    code:R -- L:github_action
    github_action:R -- L:docker

    docker:R -- L:artifact_registry
    artifact_registry:R -- L:cloud_run

    cloud_run{group}:R -- L:Streamlit{group}
```
