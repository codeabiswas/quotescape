"""
Kindle quote source for Kindle highlights.
Uses the Kindle scraper to get quotes from user's Kindle library.
"""

import json
import random
import logging
from pathlib import Path
from typing import Tuple, Dict, List, Optional
from .base import QuoteSource, Quote
from ..scrapers.kindle import KindleScraper


logger = logging.getLogger(__name__)


class KindleQuoteSource(QuoteSource):
    """Quote source that uses Kindle highlights."""
    
    def __init__(self, config, browser_name: Optional[str] = None,
                 login_timeout: int = 300, verbose: bool = False,
                 force_refresh: bool = False):
        """
        Initialize the Kindle quote source.
        
        Args:
            config: QuotescapeConfig object
            browser_name: Force specific browser for scraping
            login_timeout: Seconds to wait for login
            verbose: Enable verbose logging
            force_refresh: Force refresh of cache regardless of age
        """
        super().__init__(config)
        self.browser_name = browser_name
        self.login_timeout = login_timeout
        self.verbose = verbose
        self.force_refresh = force_refresh
        
        self.cache_path = config.project_root / "src" / "output" / "cache" / "kindle_quotebook.json"
        self.quotebook = {}
        
        # Load cached quotes if available (even if force_refresh, we load first)
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load quotes from cache file if it exists."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.quotebook = json.load(f)
                logger.info(f"Loaded {len(self.quotebook)} books from cache")
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
                self.quotebook = {}
    
    def _refresh_cache_if_needed(self) -> None:
        """Refresh the cache if it's outdated according to refresh frequency or if forced."""
        # Create scraper instance (without force_refresh - that's handled here)
        scraper = KindleScraper(
            self.config,
            browser_name=self.browser_name,
            login_timeout=self.login_timeout,
            verbose=self.verbose
        )
        
        # Check if we should refresh
        cache_outdated = scraper.is_cache_outdated()
        should_refresh = self.force_refresh or cache_outdated
        
        if should_refresh:
            if self.force_refresh:
                logger.info("🔄 Force refresh requested, starting Kindle scraping...")
            else:
                logger.info("🔄 Cache is outdated, starting Kindle scraping...")
            
            try:
                logger.info("Opening browser for Kindle scraping...")
                self.quotebook = scraper.scrape()
                logger.info(f"✅ Scraping complete! Retrieved {len(self.quotebook)} books with highlights")
            except Exception as e:
                logger.error(f"❌ Failed to refresh cache: {e}")
                # If scraping fails but we have cached data, use it
                if not self.quotebook:
                    raise
                logger.info("⚠️ Using existing cache despite refresh failure")
        else:
            logger.info("✓ Cache is up to date, no refresh needed")
    
    def get_quote(self) -> Quote:
        """
        Get a random quote from Kindle highlights.
        
        Returns:
            Quote object with text, book title, author, and optional cover URL
            
        Raises:
            ValueError: If no quotes are available
        """
        # Refresh cache if needed
        self._refresh_cache_if_needed()
        
        if not self.quotebook:
            raise ValueError(
                "No Kindle highlights found. Please ensure you have highlighted "
                "quotes in your Kindle library and that your credentials are correct."
            )
        
        # Select random book
        book_key = random.choice(list(self.quotebook.keys()))
        book_data = self.quotebook[book_key]
        
        # Extract book info
        cover_url = book_data[0] if isinstance(book_data[0], str) else ""
        quotes_list = book_data[1] if isinstance(book_data[1], list) else []
        
        if not quotes_list:
            # Try another book if this one has no quotes
            remaining_books = [k for k in self.quotebook.keys() if k != book_key]
            if remaining_books:
                book_key = random.choice(remaining_books)
                book_data = self.quotebook[book_key]
                cover_url = book_data[0] if isinstance(book_data[0], str) else ""
                quotes_list = book_data[1] if isinstance(book_data[1], list) else []
        
        if not quotes_list:
            raise ValueError("No quotes found in Kindle highlights")
        
        # Select random quote
        quote_text = random.choice(quotes_list)
        
        # Parse book title and author from key
        # Format is typically "Book Title\nBy: Author Name"
        book_title = None
        author = None
        
        if "\n" in book_key:
            parts = book_key.split("\n")
            book_title = parts[0].strip()
            if len(parts) > 1 and parts[1].startswith("By:"):
                author = parts[1][3:].strip()
        else:
            book_title = book_key.strip()
        
        return Quote(
            text=quote_text,
            author=author,
            book_title=book_title,
            book_cover_url=cover_url if cover_url else None
        )
    
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if Kindle source is properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        # Check if secrets file exists
        secrets_path = Path(self.config.kindle_source_settings.kindle_secrets_path)
        if not secrets_path.exists():
            return False, (
                f"Kindle secrets file not found at {secrets_path}. "
                f"Please create the file with your Amazon credentials:\n"
                f'{{\n  "username": "your_email@example.com",\n  "password": "your_password"\n}}'
            )
        
        # Try to load and validate secrets
        try:
            with open(secrets_path, 'r') as f:
                data = json.load(f)
                if not data.get("username") or not data.get("password"):
                    return False, "Kindle secrets file must contain both 'username' and 'password' fields"
        except json.JSONDecodeError:
            return False, f"Invalid JSON in Kindle secrets file at {secrets_path}"
        except Exception as e:
            return False, f"Error reading Kindle secrets file: {e}"
        
        # Check if we have cached data or can scrape
        if self.quotebook:
            return True, ""
        
        # No cached data, will need to scrape
        return True, "No cached Kindle highlights found. Will scrape on first run."
    
    def requires_internet(self) -> bool:
        """
        Kindle source requires internet only when refreshing cache.
        
        Returns:
            True if cache needs refresh or force refresh is set, False if using cached data
        """
        if self.force_refresh:
            return True
        
        # Create scraper to check if cache is outdated
        scraper = KindleScraper(
            self.config,
            browser_name=self.browser_name,
            login_timeout=self.login_timeout,
            verbose=self.verbose
        )
        return scraper.is_cache_outdated()