.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install dependencies
	@uv sync

.PHONY: dev
dev: ## Run development server with hot reload
	@DEV_MODE=True DEBUG=True uv run python -m src

.PHONY: run
run: ## Run production server
	@uv run python -m src

.PHONY: test
test: ## Run tests
	@uv run pytest

.PHONY: fmt
fmt: ## Format code with ruff
	@uv run ruff format .
	@uv run ruff check --fix .

.PHONY: fmt-check
fmt-check: ## Check code formatting
	@uv run ruff format --check .

.PHONY: lint
lint: ## Run linter
	@uv run ruff check .

.PHONY: types
types: ## Type check with mypy
	@uv run mypy src

.PHONY: check
check: fmt-check lint types test ## Run all checks

.PHONY: db-up
db-up: ## Start PostgreSQL with Docker (port 5434)
	@docker run -d --name chess-postgres \
		-e POSTGRES_USER=chess \
		-e POSTGRES_PASSWORD=chess \
		-e POSTGRES_DB=chess \
		-p 5434:5432 \
		postgres:16 || docker start chess-postgres

.PHONY: db-down
db-down: ## Stop PostgreSQL container
	@docker stop chess-postgres || true

.PHONY: db-migrate
db-migrate: ## Run database migrations
	@uv run alembic upgrade head

.PHONY: db-revision
db-revision: ## Create a new migration (usage: make db-revision m="description")
	@uv run alembic revision --autogenerate -m "$(m)"

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning Python build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Clean complete"
