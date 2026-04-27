.PHONY: install test lint format type-check clean plots dataset verify

install:
	pip install -e ".[dev]"

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

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .

type-check:
	mypy src/

verify: lint type-check test
	@echo "All verification checks passed!"

plots:
	python3 -m long_horizon_bench.plots --output-dir outputs/

dataset:
	python3 -m long_horizon_bench.dataset --output-dir datasets/

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run-mock:
	python3 -m long_horizon_bench.cli run --mock

all: install verify
	@echo "Project setup complete!"
