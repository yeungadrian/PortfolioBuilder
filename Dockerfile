FROM python:3.12-slim-bullseye

ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml .
RUN --mount=from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
    uv pip install -r pyproject.toml

WORKDIR /app

COPY ./app app
COPY ./sample sample

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
