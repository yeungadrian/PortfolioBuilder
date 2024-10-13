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
