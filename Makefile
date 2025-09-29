.PHONY: help
help: ## Print info about each available command in this Makefile
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# === Variables ===
SRC_DIRS := src/ tests/

# === Code Quality Tools ===

.PHONY: format
format: ## Run black code formatter
	poetry run black $(SRC_DIRS)

.PHONY: format-check
format-check: ## Check black formatting without making changes
	poetry run black --check --diff $(SRC_DIRS)

.PHONY: sort-imports
sort-imports: ## Sort imports with isort
	poetry run isort $(SRC_DIRS)

.PHONY: sort-imports-check
sort-imports-check: ## Check import sorting without making changes
	poetry run isort --check-only --diff $(SRC_DIRS)

.PHONY: clean-imports
clean-imports: ## Remove unused imports and variables with autoflake
	poetry run autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive $(SRC_DIRS)

.PHONY: clean-imports-check
clean-imports-check: ## Check for unused imports without making changes
	poetry run autoflake --remove-all-unused-imports --remove-unused-variables --check --recursive $(SRC_DIRS)

.PHONY: lint
lint: ## Run flake8 linting
	poetry run flake8 $(SRC_DIRS)

.PHONY: type-check
type-check: ## Run mypy type checking
	poetry run mypy src/

.PHONY: security-scan
security-scan: ## Run bandit security scan
	poetry run bandit -r src/ -c "pyproject.toml"

.PHONY: secrets-check
secrets-check: ## Check for new secrets against baseline
	poetry run detect-secrets-hook --baseline .secrets.baseline $(FILES)


# === Combined Commands ===

.PHONY: format-all
format-all: format sort-imports clean-imports ## Run all formatters (black, isort, autoflake)

.PHONY: check-all
check-all: format-check sort-imports-check clean-imports-check lint type-check security-scan ## Run all checks without making changes

.PHONY: fix-all
fix-all: format-all lint-fix ## Run all formatters and auto-fixable lints

.PHONY: pre-commit-manual
pre-commit-manual: format-all lint type-check security-scan ## Run all pre-commit checks manually

# === Testing ===

.PHONY: test
test: ## Run pytest tests
	poetry run pytest

.PHONY: test-cov
test-cov: ## Run pytest with coverage report
	poetry run pytest --cov=src --cov-report=html --cov-report=term

.PHONY: test-verbose
test-verbose: ## Run pytest with verbose output
	poetry run pytest -v

# === Development Setup ===

.PHONY: install-poetry
install-poetry: ## Install dependencies with poetry
	poetry install

.PHONY: install-pre-commit
install-pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

.PHONY: install
install: install-poetry install-pre-commit ## Install project requirements

.PHONY: update
update: ## Update dependencies
	poetry update

# === Pre-commit Management ===

.PHONY: pre-commit-run
pre-commit-run: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hook versions
	poetry run pre-commit autoupdate

# === Application ===

.PHONY: run
run: ## Run gitlab-tui
	poetry run gitlab-tui
