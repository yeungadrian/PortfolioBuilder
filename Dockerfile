FROM python:3.11-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_SYSTEM_PYTHON=1

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.cargo/bin/:$PATH"

# Sync the project into a new environment
COPY pyproject.toml .
RUN uv pip install -r pyproject.toml

WORKDIR /app

COPY ./app app
COPY ./data/processed data/processed

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
