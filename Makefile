# Makefile for Quotescape
# Convenience commands for common tasks

.PHONY: help install run run-random run-kindle run-custom refresh-kindle test clean

# Default target
help:
	@echo "Quotescape - Generate beautiful quote wallpapers"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install dependencies and set up the project"
	@echo "  make run            Run Quotescape with config file settings"
	@echo "  make run-random     Generate wallpaper with random quote"
	@echo "  make run-kindle     Generate wallpaper with Kindle highlight"
	@echo "  make run-custom     Generate wallpaper with custom quote"
	@echo "  make refresh-kindle Force refresh Kindle highlights cache"
	@echo "  make test           Run test suite"
	@echo "  make clean          Remove generated files and cache"
	@echo "  make help           Show this help message"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv sync; \
	else \
		pip install -r requirements.txt; \
	fi
	@python setup.py
	@echo "Installation complete!"

# Run with config file settings
run:
	@python run_quotescape.py

# Run with random quote source
run-random:
	@python run_quotescape.py --source random

# Run with Kindle source
run-kindle:
	@python run_quotescape.py --source kindle

# Run with custom source
run-custom:
	@python run_quotescape.py --source custom

# Force refresh Kindle cache
refresh-kindle:
	@echo "Refreshing Kindle highlights cache..."
	@python run_quotescape.py --source kindle --refresh-kindle

# Run tests
test:
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		python -m pytest tests/ -v 2>/dev/null || python tests/test_quotescape.py; \
	fi

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf src/output/wallpapers/*.png
	@rm -rf src/output/cache/*.json
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf .pytest_cache
	@rm -rf *.pyc */*.pyc */*/*.pyc
	@echo "Clean complete!"

# Development shortcuts
.PHONY: dev-install dev-test lint format

# Install development dependencies
dev-install:
	@pip install -r requirements-dev.txt

# Run tests with coverage
dev-test:
	@pytest tests/ -v --cov=quotescape --cov-report=html --cov-report=term

# Run linter
lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/; \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 src/; \
	else \
		echo "No linter found. Install ruff or flake8."; \
	fi

# Format code
format:
	@if command -v black >/dev/null 2>&1; then \
		black src/; \
	else \
		echo "Black not found. Install with: pip install black"; \
	fi