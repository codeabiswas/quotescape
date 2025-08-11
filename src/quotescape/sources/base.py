"""
Base class for quote sources.
Defines the interface that all quote sources must implement.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Quote:
    """Represents a quote with its metadata."""
    text: str
    author: Optional[str] = None
    book_title: Optional[str] = None
    book_cover_url: Optional[str] = None
    
    def get_author_display(self) -> str:
        """Get the author name for display, defaulting to 'Unknown' if not set."""
        return self.author if self.author else "Unknown"


class QuoteSource(ABC):
    """Abstract base class for all quote sources."""
    
    def __init__(self, config):
        """
        Initialize the quote source with configuration.
        
        Args:
            config: QuotescapeConfig object containing all settings
        """
        self.config = config
    
    @abstractmethod
    def get_quote(self) -> Quote:
        """
        Get a quote from this source.
        
        Returns:
            Quote object containing the quote text and metadata
            
        Raises:
            Exception: If unable to retrieve a quote
        """
        pass
    
    @abstractmethod
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if this source is available and properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
            - is_available: True if source can be used
            - error_message: Description of why source is unavailable (empty if available)
        """
        pass
    
    def requires_internet(self) -> bool:
        """
        Check if this source requires internet connection.
        
        Returns:
            True if internet is required, False otherwise
        """
        return False