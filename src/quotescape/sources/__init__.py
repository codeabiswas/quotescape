# src/quotescape/sources/__init__.py
"""Quote sources for Quotescape."""

from .base import QuoteSource, Quote
from .random import RandomQuoteSource
from .custom import CustomQuoteSource
from .kindle import KindleQuoteSource

__all__ = [
    "QuoteSource",
    "Quote", 
    "RandomQuoteSource",
    "CustomQuoteSource",
    "KindleQuoteSource"
]
