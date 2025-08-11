# Makefile for Quotescape development tasks

.PHONY: help setup install clean test run run-random run-kindle run-custom lint format check-format

# Default target
help:
	@echo "Quotescape Development Commands"
	@echo "================================"
	@echo "make setup        - Complete setup (download fonts, create dirs, install deps)"
	@echo "make install      - Install Python dependencies"
	@echo "make clean        - Clean generated files and caches"
	@echo "make test         - Run tests"
	@echo "make test-api     - Test The Quotes Hub API"
	@echo "make run          - Run Quotescape (uses config file settings)"
	@echo "make run-random   - Run with random quotes (overrides config)"
	@echo "make run-kindle   - Run with Kindle highlights (overrides config)"
	@echo "make run-custom   - Run with custom quotes (overrides config)"
	@echo "make lint         - Run code linters"
	@echo "make format       - Format code with black"
	@echo "make check-format - Check code formatting"

# Setup everything
setup:
	@echo "🎨 Setting up Quotescape..."
	python setup.py

# Install dependencies
install:
	@if command -v uv >/dev/null 2>&1; then \
		echo "📦 Installing with uv..."; \
		uv sync; \
	else \
		echo "📦 Installing with pip..."; \
		pip install -r requirements.txt; \
	fi

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf src/output/wallpapers/*.png
	rm -rf src/output/cache/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	@echo "✅ Clean complete!"

# Run tests
test:
	@if command -v uv >/dev/null 2>&1; then \
		echo "🧪 Running tests with uv..."; \
		uv run pytest tests/ -v; \
	else \
		echo "🧪 Running tests with pytest..."; \
		python -m pytest tests/ -v; \
	fi

# Run with default settings
run:
	@if command -v uv >/dev/null 2>&1; then \
		uv run python run_quotescape.py; \
	else \
		python run_quotescape.py; \
	fi

# Run with random quotes (using CLI override)
run-random:
	@if command -v uv >/dev/null 2>&1; then \
		uv run python run_quotescape.py --source random; \
	else \
		python run_quotescape.py --source random; \
	fi

# Run with Kindle highlights (using CLI override)
run-kindle:
	@if [ ! -f kindle_secrets.json ]; then \
		echo "❌ Error: kindle_secrets.json not found!"; \
		echo "Create it with your Amazon credentials:"; \
		echo '{"username": "email@example.com", "password": "password"}'; \
		exit 1; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		uv run python run_quotescape.py --source kindle; \
	else \
		python run_quotescape.py --source kindle; \
	fi

# Run with custom quotes (using CLI override)
run-custom:
	@if [ ! -f custom_quotebook.json ]; then \
		echo "❌ Error: custom_quotebook.json not found!"; \
		echo "Creating example custom quotebook..."; \
		cp examples/custom_quotebook.json . 2>/dev/null || echo '{"Author": ["Quote"]}' > custom_quotebook.json; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		uv run python run_quotescape.py --source custom; \
	else \
		python run_quotescape.py --source custom; \
	fi

# Test The Quotes Hub API
test-api:
	@if [ -f test_api.py ]; then \
		python test_api.py; \
	else \
		echo "Testing The Quotes Hub API..."; \
		python -c "import requests, json; r=requests.get('https://thequoteshub.com/api/random-quote'); d=r.json(); print('✅ API Working!'); print(f\"Quote: {d.get('text', 'N/A')[:80]}...\"); print(f\"Author: {d.get('author', 'N/A')}\")"; \
	fi

# Lint code
lint:
	@if command -v ruff >/dev/null 2>&1; then \
		echo "🔍 Linting with ruff (fast)..."; \
		ruff check src/ tests/; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "🔍 Linting with flake8..."; \
		uv run flake8 src/ tests/ --max-line-length=100; \
		echo "🔍 Type checking with mypy..."; \
		uv run mypy src/quotescape/; \
	else \
		echo "🔍 Linting with flake8..."; \
		python -m flake8 src/ tests/ --max-line-length=100; \
		echo "🔍 Type checking with mypy..."; \
		python -m mypy src/quotescape/; \
	fi

# Format code
format:
	@if command -v ruff >/dev/null 2>&1; then \
		echo "✨ Formatting with ruff..."; \
		ruff format src/ tests/; \
		ruff check --fix src/ tests/; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "✨ Formatting with black..."; \
		uv run black src/ tests/; \
	else \
		echo "✨ Formatting with black..."; \
		python -m black src/ tests/; \
	fi

# Check formatting
check-format:
	@if command -v ruff >/dev/null 2>&1; then \
		echo "🔍 Checking formatting with ruff..."; \
		ruff format --check src/ tests/; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "🔍 Checking formatting..."; \
		uv run black --check src/ tests/; \
	else \
		echo "🔍 Checking formatting..."; \
		python -m black --check src/ tests/; \
	fi

# Development install (editable)
dev-install:
	@if command -v uv >/dev/null 2>&1; then \
		echo "📦 Installing in development mode with uv..."; \
		uv sync --dev; \
	else \
		echo "📦 Installing in development mode with pip..."; \
		pip install -e .; \
		pip install pytest pytest-cov black flake8 mypy; \
	fi

# Show current configuration
show-config:
	@echo "📋 Current Configuration:"
	@echo "========================"
	@if [ -f quotescape.yaml ]; then \
		cat quotescape.yaml; \
	else \
		echo "Using default configuration (no quotescape.yaml found)"; \
	fi

# Generate coverage report
coverage:
	@if command -v uv >/dev/null 2>&1; then \
		uv run pytest tests/ --cov=quotescape --cov-report=html --cov-report=term; \
	else \
		python -m pytest tests/ --cov=quotescape --cov-report=html --cov-report=term; \
	fi
	@echo "📊 Coverage report generated in htmlcov/index.html"