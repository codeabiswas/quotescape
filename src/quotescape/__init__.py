# src/quotescape/__init__.py
"""
Quotescape - Generate beautiful quote wallpapers for your desktop.

A cross-platform application that creates inspiring wallpapers from quotes.
Supports random quotes from Quotable API, Kindle highlights, and custom quotes.
"""

from .main import main, __version__

__all__ = ["main", "__version__"]