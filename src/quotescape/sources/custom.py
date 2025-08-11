"""
Custom quote source for user-provided quotes.
Reads quotes from a JSON file in the format specified by the user.
"""

import json
import random
from pathlib import Path
from typing import Tuple, Dict, List
from .base import QuoteSource, Quote


class CustomQuoteSource(QuoteSource):
    """Quote source that reads from user-provided JSON file."""
    
    def __init__(self, config):
        """Initialize the custom quote source."""
        super().__init__(config)
        self.quotebook_path = Path(config.custom_source_settings.custom_quotebook_path)
        self.quotebook = {}
        self._load_quotebook()
    
    def _load_quotebook(self) -> None:
        """
        Load the custom quotebook from JSON file.
        
        Expected format:
        {
            "author1": ["quote1", "quote2"],
            "author2": ["quote1", "quote2"]
        }
        """
        if self.quotebook_path.exists():
            try:
                with open(self.quotebook_path, 'r', encoding='utf-8') as f:
                    self.quotebook = json.load(f)
                    self._validate_quotebook()
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in custom quotebook at {self.quotebook_path}: {e}"
                )
            except Exception as e:
                raise Exception(
                    f"Error reading custom quotebook at {self.quotebook_path}: {e}"
                )
    
    def _validate_quotebook(self) -> None:
        """Validate the structure of the loaded quotebook."""
        if not isinstance(self.quotebook, dict):
            raise ValueError(
                "Custom quotebook must be a JSON object with authors as keys "
                "and arrays of quotes as values"
            )
        
        for author, quotes in self.quotebook.items():
            if not isinstance(author, str):
                raise ValueError(f"Author name must be a string, got: {type(author)}")
            if not isinstance(quotes, list):
                raise ValueError(f"Quotes for {author} must be an array")
            if not quotes:
                raise ValueError(f"Author {author} has no quotes")
            for quote in quotes:
                if not isinstance(quote, str):
                    raise ValueError(f"All quotes must be strings, got: {type(quote)}")
    
    def get_quote(self) -> Quote:
        """
        Get a random quote from the custom quotebook.
        
        Returns:
            Quote object with text and author
            
        Raises:
            ValueError: If quotebook is empty or invalid
        """
        if not self.quotebook:
            raise ValueError(
                f"Custom quotebook is empty. Please add quotes to {self.quotebook_path}"
            )
        
        # Select random author
        author = random.choice(list(self.quotebook.keys()))
        
        # Select random quote from that author
        quote_text = random.choice(self.quotebook[author])
        
        return Quote(
            text=quote_text,
            author=author
        )
    
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if custom quotebook exists and is valid.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        if not self.quotebook_path.exists():
            return False, (
                f"Custom quotebook not found at {self.quotebook_path}. "
                f"Please create the file with your quotes in JSON format:\n"
                f'{{\n  "Author Name": ["quote 1", "quote 2"],\n  ...\n}}'
            )
        
        try:
            self._load_quotebook()
            if not self.quotebook:
                return False, f"Custom quotebook at {self.quotebook_path} is empty"
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def add_quote(self, author: str, quote: str) -> None:
        """
        Add a new quote to the quotebook.
        
        Args:
            author: Name of the quote author
            quote: The quote text
        """
        if author not in self.quotebook:
            self.quotebook[author] = []
        
        if quote not in self.quotebook[author]:
            self.quotebook[author].append(quote)
            self._save_quotebook()
    
    def remove_quote(self, author: str, quote: str) -> None:
        """
        Remove a quote from the quotebook.
        
        Args:
            author: Name of the quote author
            quote: The quote text to remove
            
        Raises:
            KeyError: If author or quote doesn't exist
        """
        if author not in self.quotebook:
            raise KeyError(f"Author '{author}' not found in quotebook")
        
        if quote not in self.quotebook[author]:
            raise KeyError(f"Quote not found for author '{author}'")
        
        self.quotebook[author].remove(quote)
        
        # Remove author if no quotes left
        if not self.quotebook[author]:
            del self.quotebook[author]
        
        self._save_quotebook()
    
    def _save_quotebook(self) -> None:
        """Save the quotebook back to JSON file."""
        # Ensure directory exists
        self.quotebook_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.quotebook_path, 'w', encoding='utf-8') as f:
            json.dump(self.quotebook, f, indent=2, ensure_ascii=False)