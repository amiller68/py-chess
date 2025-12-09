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
types: ## Type check with ty
	@uv run ty check src

.PHONY: check
check: fmt-check lint types test ## Run all checks

.PHONY: db
db: ## Database management (up, down, migrate, status, etc.)
	@./bin/db.sh $(filter-out $@,$(MAKECMDGOALS))

# Catch additional arguments to db command
%:
	@:

.PHONY: tfc
tfc: ## Terraform Cloud management (up, status)
	@./bin/tfc $(filter-out $@,$(MAKECMDGOALS))

.PHONY: iac
iac: ## Infrastructure management (production init, production apply, etc.)
	@./bin/iac $(filter-out $@,$(MAKECMDGOALS))

.PHONY: kamal
kamal: ## Kamal deployment (chess production deploy, chess production logs, etc.)
	@./bin/kamal $(filter-out $@,$(MAKECMDGOALS))

.PHONY: deploy
deploy: ## Deploy to production (shortcut for: kamal chess production deploy)
	@./bin/kamal chess production deploy

.PHONY: docker-build
docker-build: ## Build Docker image
	@docker build -t py-chess .

.PHONY: docker-run
docker-run: ## Run with Docker Compose (app + postgres)
	@docker compose up --build

.PHONY: docker-down
docker-down: ## Stop Docker Compose services
	@docker compose down

.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning Python build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ty_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Clean complete"
