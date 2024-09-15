.PHONY: sync format test  help

setup:
	@uv sync --all-extras --dev

format:
	@uv run -- pre-commit run --all-files

test:
	@uv run -- coverage run -m pytest tests && uv run -- coverage report

help:
	@echo "Available targets:"
	@echo "  sync   - Sync dependencies and extras"
	@echo "  format - Run pre-commit hooks on all files"
	@echo "  test   - Run pytest tests"
