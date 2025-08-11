"""
Kindle highlights scraper using Selenium.
Scrapes user's Kindle highlights from Amazon's Kindle Notebook.
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


logger = logging.getLogger(__name__)


class KindleScraper:
    """Scrapes Kindle highlights from Amazon's Kindle Notebook."""
    
    KINDLE_URL = "https://read.amazon.com/kp/notebook"
    
    def __init__(self, config, browser_name: Optional[str] = None, 
                 login_timeout: int = 300, verbose: bool = False):
        """
        Initialize the Kindle scraper.
        
        Args:
            config: QuotescapeConfig object
            browser_name: Force specific browser (chrome, firefox, edge, safari)
            login_timeout: Seconds to wait for login completion
            verbose: Enable verbose logging
        """
        self.config = config
        self.browser_name = browser_name
        self.login_timeout = login_timeout
        self.verbose = verbose
        
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        self.driver = None
        self.quotebook = {}
        
        # Paths
        self.secrets_path = Path(config.kindle_source_settings.kindle_secrets_path)
        self.cache_path = config.project_root / "src" / "output" / "cache" / "kindle_quotebook.json"
        
    def _get_webdriver(self) -> webdriver:
        """
        Get appropriate webdriver based on platform and availability.
        
        Returns:
            Configured webdriver instance
            
        Raises:
            Exception: If no suitable browser is found
        """
        browsers = []
        
        if self.browser_name:
            # User specified a browser
            browsers = [self.browser_name.lower()]
        else:
            # Try browsers in order of preference
            import platform
            if platform.system() == "Darwin":  # macOS
                browsers = ["chrome", "firefox", "edge", "safari"]
            else:
                browsers = ["chrome", "edge", "firefox"]
        
        for browser in browsers:
            try:
                # Use match/case for cleaner browser setup (Python 3.11+)
                match browser:
                    case "chrome":
                        from selenium.webdriver.chrome.options import Options
                        options = Options()
                        options.add_argument("--disable-blink-features=AutomationControlled")
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                        return webdriver.Chrome(options=options)
                    
                    case "firefox":
                        from selenium.webdriver.firefox.options import Options
                        options = Options()
                        options.set_preference("dom.webdriver.enabled", False)
                        options.set_preference('useAutomationExtension', False)
                        return webdriver.Firefox(options=options)
                    
                    case "edge":
                        from selenium.webdriver.edge.options import Options
                        options = Options()
                        options.add_argument("--disable-blink-features=AutomationControlled")
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                        return webdriver.Edge(options=options)
                    
                    case "safari":
                        # Safari requires "Allow Remote Automation" to be enabled in Developer menu
                        return webdriver.Safari()
                    
            except Exception as e:
                if self.verbose:
                    logger.debug(f"Browser {browser} not available: {e}")
                continue
        
        raise Exception(
            "No suitable browser found. Please install Chrome, Firefox, or Edge, "
            "or enable Safari's 'Allow Remote Automation' in Developer menu."
        )
    
    def _load_credentials(self) -> Tuple[str, str]:
        """
        Load Amazon credentials from secrets file.
        
        Returns:
            Tuple of (username, password)
            
        Raises:
            FileNotFoundError: If secrets file doesn't exist
            ValueError: If secrets file is invalid
        """
        if not self.secrets_path.exists():
            raise FileNotFoundError(
                f"Kindle secrets file not found at {self.secrets_path}. "
                f"Please create the file with your Amazon credentials:\n"
                f'{{\n  "username": "your_email@example.com",\n  "password": "your_password"\n}}'
            )
        
        try:
            with open(self.secrets_path, 'r') as f:
                data = json.load(f)
                
            username = data.get("username", "").strip()
            password = data.get("password", "").strip()
            
            if not username or not password:
                raise ValueError("Username and password must not be empty")
                
            return username, password
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in kindle secrets file: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required field in kindle secrets file: {e}")
    
    def _login(self, username: str, password: str) -> None:
        """
        Log in to Amazon Kindle Notebook.
        
        Args:
            username: Amazon account email
            password: Amazon account password
            
        Raises:
            TimeoutException: If login times out
        """
        logger.info("Navigating to Kindle Notebook...")
        self.driver.get(self.KINDLE_URL)
        
        try:
            # Wait for and fill email field
            email_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(username)
            
            # Click continue
            continue_button = self.driver.find_element(By.ID, "continue")
            continue_button.click()
            
            # Wait for and fill password field
            password_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.clear()
            password_field.send_keys(password)
            
            # Click sign in
            signin_button = self.driver.find_element(By.ID, "signInSubmit")
            signin_button.click()
            
            # Handle potential 2FA
            logger.info("Logging in... If 2FA is required, please complete it in the browser.")
            
            # Wait for successful login (presence of notebook elements)
            WebDriverWait(self.driver, self.login_timeout).until(
                EC.presence_of_element_located((By.ID, "kp-notebook-library"))
            )
            
            logger.info("Successfully logged in to Kindle Notebook")
            
        except TimeoutException:
            # Check if we're on a 2FA page or other authentication page
            current_url = self.driver.current_url
            if "signin" in current_url or "ap/mfa" in current_url:
                print(f"\n{'='*60}")
                print("ACTION REQUIRED: Please complete the login process in the browser.")
                print("This may include 2FA verification or CAPTCHA.")
                print(f"You have {self.login_timeout} seconds to complete the login.")
                print(f"{'='*60}\n")
                
                # Wait for successful login
                try:
                    WebDriverWait(self.driver, self.login_timeout).until(
                        EC.presence_of_element_located((By.ID, "kp-notebook-library"))
                    )
                    logger.info("Login completed successfully")
                except TimeoutException:
                    raise TimeoutException(
                        f"Login timed out after {self.login_timeout} seconds. "
                        "Please try again or increase timeout with --login-timeout flag."
                    )
            else:
                raise TimeoutException("Unable to log in to Kindle Notebook")
    
    def _scrape_quotes(self) -> Dict:
        """
        Scrape all quotes from Kindle Notebook.
        
        Returns:
            Dictionary with book info as keys and (cover_url, quotes) as values
        """
        quotebook = {}
        
        try:
            # Wait for library to load
            library = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "kp-notebook-library"))
            )
            
            # Get all book entries
            book_entries = library.find_elements(By.CSS_SELECTOR, "div.kp-notebook-library-book")
            
            if not book_entries:
                # Try alternative selector
                book_entries = library.find_elements(By.TAG_NAME, "div")
                book_entries = [b for b in book_entries if b.text.strip()]
            
            logger.info(f"Found {len(book_entries)} books with highlights")
            
            for book_entry in book_entries:
                try:
                    book_text = book_entry.text.strip()
                    if not book_text:
                        continue
                    
                    # Click on the book to load its highlights
                    book_entry.click()
                    time.sleep(2)  # Wait for content to load
                    
                    # Get book cover URL
                    cover_url = self._get_book_cover()
                    
                    # Get all highlights
                    quotes = self._get_book_quotes()
                    
                    if quotes:
                        # Use the book text as key (contains title and author)
                        quotebook[book_text] = [cover_url, quotes]
                        logger.info(f"Scraped {len(quotes)} quotes from: {book_text}")
                    
                except Exception as e:
                    logger.warning(f"Error processing book: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping quotes: {e}")
            raise
        
        return quotebook
    
    def _get_book_cover(self) -> str:
        """
        Get the book cover URL from the current page.
        
        Returns:
            Book cover URL or empty string if not found
        """
        try:
            annotations_pane = self.driver.find_element(By.ID, "annotations")
            cover_img = annotations_pane.find_element(By.CLASS_NAME, "kp-notebook-cover-image-border")
            cover_url = cover_img.get_attribute("src")
            
            if cover_url:
                # Get higher resolution version
                cover_url = cover_url.replace("_SY160", "_SY2400")
                return cover_url
                
        except Exception as e:
            logger.debug(f"Could not get book cover: {e}")
        
        return ""
    
    def _get_book_quotes(self) -> List[str]:
        """
        Get all quotes from the current book page.
        
        Returns:
            List of quote texts
        """
        quotes = []
        
        try:
            # Wait for annotations to load
            annotations = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "kp-notebook-annotations"))
            )
            
            # Get all highlight elements
            highlight_elements = annotations.find_elements(By.ID, "highlight")
            
            for element in highlight_elements:
                text = element.text.strip()
                if text:
                    quotes.append(text)
            
        except Exception as e:
            logger.warning(f"Error getting quotes: {e}")
        
        return quotes
    
    def scrape(self) -> Dict:
        """
        Main method to scrape Kindle highlights.
        
        Returns:
            Dictionary of scraped quotes
            
        Raises:
            Exception: If scraping fails
        """
        try:
            logger.info("Starting Kindle scraper...")
            
            # Load credentials
            username, password = self._load_credentials()
            
            # Start browser
            logger.info("Starting browser...")
            self.driver = self._get_webdriver()
            
            # Login
            self._login(username, password)
            
            # Scrape quotes
            logger.info("Scraping quotes...")
            self.quotebook = self._scrape_quotes()
            
            # Save to cache
            self._save_cache()
            
            return self.quotebook
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
    
    def _save_cache(self) -> None:
        """Save scraped quotes to cache file."""
        # Ensure cache directory exists
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.quotebook, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.quotebook)} books to cache: {self.cache_path}")
    
    def is_cache_outdated(self) -> bool:
        """
        Check if the cache needs to be refreshed based on refresh frequency.
        
        Returns:
            True if cache should be refreshed, False otherwise
        """
        if not self.cache_path.exists():
            return True
        
        frequency = self.config.kindle_source_settings.refresh_frequency
        
        # Handle "always" refresh - never use cache
        if frequency == "always":
            return True
        
        # Get last modified time
        mtime = datetime.fromtimestamp(self.cache_path.stat().st_mtime)
        now = datetime.now()
        
        # Use match/case for cleaner frequency checking (Python 3.11+)
        match frequency:
            case "daily":
                return (now - mtime) >= timedelta(days=1)
            case "weekly":
                return (now - mtime) >= timedelta(weeks=1)
            case "monthly":
                # Check if we're in a new month
                return (now.year, now.month) != (mtime.year, mtime.month)
            case "quarterly":
                # Check if we're in a new quarter
                current_quarter = (now.month - 1) // 3
                mtime_quarter = (mtime.month - 1) // 3
                return (now.year, current_quarter) != (mtime.year, mtime_quarter)
            case "biannually":
                # Check if we're in a new half-year
                current_half = now.month <= 6
                mtime_half = mtime.month <= 6
                return (now.year, current_half) != (mtime.year, mtime_half)
            case "annually":
                return now.year != mtime.year
            case _:
                # Default to monthly if invalid frequency
                return (now.year, now.month) != (mtime.year, mtime.month)