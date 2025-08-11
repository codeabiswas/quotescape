"""
Random quote source using The Quotes Hub API.
Fetches random quotes from the internet.
"""

import json
import requests
from typing import Tuple
from .base import QuoteSource, Quote


class RandomQuoteSource(QuoteSource):
    """Quote source that fetches random quotes from The Quotes Hub API."""
    
    # The Quotes Hub API - simple and reliable
    API_URL = "https://thequoteshub.com/api/random-quote"
    TIMEOUT_SECONDS = 10
    
    def __init__(self, config):
        """Initialize the random quote source."""
        super().__init__(config)
    
    def get_quote(self) -> Quote:
        """
        Fetch a random quote from The Quotes Hub API.
        
        The API returns JSON with format:
        {
            "text": "quote text here",
            "author": "Author Name",
            "topic": "Category"
        }
        
        Returns:
            Quote object with text and author
            
        Raises:
            requests.RequestException: If API request fails
            TimeoutError: If request times out
            ValueError: If API returns invalid data
        """
        try:
            response = requests.get(self.API_URL, timeout=self.TIMEOUT_SECONDS)
            response.raise_for_status()
            
            data = response.json()
            
            # The Quotes Hub format: {"text": "...", "author": "...", "topic": "..."}
            text = data.get('text', '')
            author = data.get('author', None)
            # topic = data.get('topic', None)  # Available if we want to use it later
            
            if not text:
                raise ValueError("No quote text in API response")
            
            # Clean up author name if present
            if author:
                author = author.strip()
                # Handle empty or "Unknown" authors
                if author in ["", "Unknown", "unknown", "Anonymous"]:
                    author = None
            
            return Quote(
                text=text.strip(),
                author=author
            )
            
        except requests.Timeout:
            raise TimeoutError(
                f"Request to The Quotes Hub API timed out after {self.TIMEOUT_SECONDS} seconds. "
                "Please check your internet connection and try again."
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "Unable to connect to The Quotes Hub API. "
                "Please check your internet connection and try again."
            )
        except requests.RequestException as e:
            raise Exception(f"Error fetching quote from The Quotes Hub API: {e}")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from The Quotes Hub API: {e}")
    
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if The Quotes Hub API is accessible.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            # Try a quick request with short timeout
            response = requests.get(self.API_URL, timeout=3)
            response.raise_for_status()
            
            # Verify it returns valid JSON with expected fields
            data = response.json()
            if 'text' in data and 'author' in data:
                return True, ""
            else:
                return False, "API returned unexpected format"
                
        except requests.RequestException as e:
            return False, f"The Quotes Hub API is not accessible: {e}"
    
    def requires_internet(self) -> bool:
        """Random quotes always require internet connection."""
        return True