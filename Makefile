sync:
	uv sync --all-extras --dev

format:
	uv run -- pre-commit run --all-files

test:
	uv run -- python -m pytest tests
