.PHONY: install test lint format type-check clean plots dataset docs all verify

# Installation
install:
	pip install -e ".[dev]"

install-prod:
	pip install -e .

# Testing
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=src/long_horizon_bench --cov-report=html --cov-report=term

test-models:
	pytest tests/test_models.py -v

test-tools:
	pytest tests/test_tools.py -v

test-runner:
	pytest tests/test_runner.py -v

# Linting and formatting
lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .

type-check:
	mypy src/

# Verification (all quality checks)
verify: lint type-check test
	@echo "✅ All verification checks passed!"

# Plots
plots:
	python -m long_horizon_bench.plots --output-dir outputs/

# Dataset generation
dataset:
	python -m long_horizon_bench.dataset --output-dir datasets/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Run benchmark
run:
	python -m long_horizon_bench.cli run --config config.yaml

run-mock:
	python -m long_horizon_bench.cli run --mock --config config.yaml

# Documentation
docs:
	@echo "See docs/ directory for documentation"

# Full setup
all: install verify
	@echo "✅ Project setup complete!"
