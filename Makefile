.PHONY: help install install-dev test test-quick test-gpu lint format type-check clean build docker run benchmark docs

# Default target
.DEFAULT_GOAL := help

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)fsociety 4.0 - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install package in development mode
	@echo "$(CYAN)Installing fsociety...$(NC)"
	pip install -e .
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev: ## Install package with development dependencies
	@echo "$(CYAN)Installing fsociety with development dependencies...$(NC)"
	pip install -e ".[all]"
	pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

install-ai: ## Install package with AI dependencies
	@echo "$(CYAN)Installing fsociety with AI features...$(NC)"
	pip install -e ".[ai]"
	@echo "$(GREEN)✓ AI features installed$(NC)"

install-gpu: ## Install package with GPU support
	@echo "$(CYAN)Installing fsociety with GPU support...$(NC)"
	pip install -e ".[ai,gpu]"
	@echo "$(GREEN)✓ GPU support installed$(NC)"

test: ## Run all tests
	@echo "$(CYAN)Running all tests...$(NC)"
	pytest -v
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-quick: ## Run quick tests only
	@echo "$(CYAN)Running quick tests...$(NC)"
	pytest tests/test_core.py -v
	@echo "$(GREEN)✓ Quick tests complete$(NC)"

test-integration: ## Run integration tests
	@echo "$(CYAN)Running integration tests...$(NC)"
	pytest tests/test_integration.py -v
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-gpu: ## Run GPU tests
	@echo "$(CYAN)Running GPU tests...$(NC)"
	pytest tests/test_gpu.py -v
	@echo "$(GREEN)✓ GPU tests complete$(NC)"

test-cov: ## Run tests with coverage
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	pytest --cov=fsociety --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated at htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(CYAN)Running tests in watch mode...$(NC)"
	pytest-watch

benchmark: ## Run performance benchmarks
	@echo "$(CYAN)Running benchmarks...$(NC)"
	pytest --benchmark-only --benchmark-autosave
	@echo "$(GREEN)✓ Benchmarks complete$(NC)"

lint: ## Run linting checks
	@echo "$(CYAN)Running linting...$(NC)"
	@ruff check fsociety tests && echo "$(GREEN)✓ Ruff passed$(NC)" || echo "$(RED)✗ Ruff failed$(NC)"
	@black --check fsociety tests && echo "$(GREEN)✓ Black passed$(NC)" || echo "$(RED)✗ Black failed$(NC)"

lint-fix: ## Fix linting issues
	@echo "$(CYAN)Fixing linting issues...$(NC)"
	ruff check fsociety tests --fix
	black fsociety tests
	@echo "$(GREEN)✓ Linting fixed$(NC)"

format: ## Format code with black
	@echo "$(CYAN)Formatting code...$(NC)"
	black fsociety tests
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checking
	@echo "$(CYAN)Running type checks...$(NC)"
	mypy fsociety --install-types --non-interactive
	@echo "$(GREEN)✓ Type checks complete$(NC)"

security: ## Run security checks
	@echo "$(CYAN)Running security checks...$(NC)"
	bandit -r fsociety
	safety check
	@echo "$(GREEN)✓ Security checks complete$(NC)"

pre-commit: ## Run pre-commit hooks
	@echo "$(CYAN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks complete$(NC)"

clean: ## Clean build artifacts
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

build: clean ## Build distribution packages
	@echo "$(CYAN)Building distribution packages...$(NC)"
	python -m build
	@echo "$(GREEN)✓ Build complete$(NC)"

publish-test: build ## Publish to Test PyPI
	@echo "$(CYAN)Publishing to Test PyPI...$(NC)"
	twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Published to Test PyPI$(NC)"

publish: build ## Publish to PyPI
	@echo "$(CYAN)Publishing to PyPI...$(NC)"
	twine upload dist/*
	@echo "$(GREEN)✓ Published to PyPI$(NC)"

docker-build: ## Build Docker image
	@echo "$(CYAN)Building Docker image...$(NC)"
	docker build -t fsociety:latest .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-build-gpu: ## Build GPU Docker image
	@echo "$(CYAN)Building GPU Docker image...$(NC)"
	docker build --target gpu -t fsociety:gpu .
	@echo "$(GREEN)✓ GPU Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(CYAN)Running Docker container...$(NC)"
	docker run -it --rm fsociety:latest

docker-run-gpu: ## Run GPU Docker container
	@echo "$(CYAN)Running GPU Docker container...$(NC)"
	docker run --gpus all -it --rm fsociety:gpu

run: ## Run fsociety
	@python -m fsociety

run-ai: ## Run fsociety with AI
	@python -m fsociety --ai

run-examples: ## Run example scripts
	@python examples/basic_usage.py

docs-serve: ## Serve documentation locally
	@echo "$(CYAN)Serving documentation...$(NC)"
	mkdocs serve

docs-build: ## Build documentation
	@echo "$(CYAN)Building documentation...$(NC)"
	mkdocs build
	@echo "$(GREEN)✓ Documentation built at site/$(NC)"

docs-deploy: ## Deploy documentation to GitHub Pages
	@echo "$(CYAN)Deploying documentation...$(NC)"
	mkdocs gh-deploy
	@echo "$(GREEN)✓ Documentation deployed$(NC)"

check-gpu: ## Check GPU availability
	@echo "$(CYAN)Checking GPU availability...$(NC)"
	@python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('MPS available:', torch.backends.mps.is_available())" 2>/dev/null || echo "$(YELLOW)PyTorch not installed$(NC)"
	@which nvidia-smi > /dev/null && nvidia-smi || echo "$(YELLOW)nvidia-smi not found$(NC)"

check-deps: ## Check dependencies
	@echo "$(CYAN)Checking dependencies...$(NC)"
	pip list | grep -E "(fsociety|torch|rich|aiohttp)"

version: ## Show version
	@python -c "from fsociety.__version__ import __version__; print(__version__)"

info: ## Show system information
	@echo "$(CYAN)System Information:$(NC)"
	@python --version
	@echo "fsociety: $$(python -c 'from fsociety.__version__ import __version__; print(__version__)')"
	@echo "Platform: $$(python -c 'import platform; print(platform.system())')"

all: lint type-check test ## Run all checks

ci: lint type-check test-cov ## Run CI pipeline

# Development workflow targets
dev-setup: install-dev ## Complete development setup
	@echo "$(GREEN)✓ Development environment is ready!$(NC)"
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  1. Run tests: make test"
	@echo "  2. Run fsociety: make run"
	@echo "  3. View help: make help"

quick-check: lint-fix test-quick ## Quick development check
	@echo "$(GREEN)✓ Quick check passed$(NC)"

full-check: lint type-check test security ## Full quality check
	@echo "$(GREEN)✓ All checks passed$(NC)"

# Release workflow
release-patch: ## Bump patch version and release
	@echo "$(CYAN)Releasing patch version...$(NC)"
	bump2version patch
	git push && git push --tags

release-minor: ## Bump minor version and release
	@echo "$(CYAN)Releasing minor version...$(NC)"
	bump2version minor
	git push && git push --tags

release-major: ## Bump major version and release
	@echo "$(CYAN)Releasing major version...$(NC)"
	bump2version major
	git push && git push --tags