#!/usr/bin/env python
"""
Simple runner script for Quotescape.

Usage:
    python run_quotescape.py                                    # Use config file source
    python run_quotescape.py --source random                    # Override with random quotes
    python run_quotescape.py --source kindle                    # Override with Kindle highlights
    python run_quotescape.py --source custom                    # Override with custom quotes
    python run_quotescape.py --source kindle --refresh-kindle   # Force refresh Kindle cache and generate
    python run_quotescape.py --help                             # Show all options
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run main
from quotescape.main import main

if __name__ == "__main__":
    main()