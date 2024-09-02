.PHONY: sync format test  help

sync:
	@uv sync --all-extras --dev

format:
	@uv run -- pre-commit run --all-files

test:
	@uv run -- python -m pytest tests

help:
	@echo "Available targets:"
	@echo "  sync   - Sync dependencies and extras"
	@echo "  format - Run pre-commit hooks on all files"
	@echo "  test   - Run pytest tests"
