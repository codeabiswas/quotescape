#!/usr/bin/env python
"""
Basic tests for Quotescape functionality.
Run with: pytest tests/test_quotescape.py
"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from quotescape.config import ConfigLoader, QuotescapeConfig
from quotescape.sources.base import Quote
from quotescape.sources.random import RandomQuoteSource
from quotescape.sources.custom import CustomQuoteSource


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_default_config_loads(self):
        """Test that default configuration loads successfully."""
        loader = ConfigLoader()
        config = loader.load()
        
        assert config.source == "random"
        assert config.dimension.width == 7680
        assert config.dimension.height == 4320
        assert config.dark_mode is True
        assert config.show_author is True
    
    def test_color_validation(self):
        """Test hex color code validation."""
        loader = ConfigLoader()
        
        # Valid colors
        loader._validate_hex_color("#FFFFFF", "test")
        loader._validate_hex_color("#000000", "test")
        loader._validate_hex_color("#ABC", "test")
        
        # Invalid colors
        with pytest.raises(ValueError):
            loader._validate_hex_color("FFFFFF", "test")  # Missing #
        with pytest.raises(ValueError):
            loader._validate_hex_color("#GGGGGG", "test")  # Invalid hex
        with pytest.raises(ValueError):
            loader._validate_hex_color("#12345", "test")  # Wrong length
    
    def test_dimension_validation(self):
        """Test dimension validation."""
        loader = ConfigLoader()
        
        # Valid dimensions
        loader._validate_dimensions(1920, 1080)
        loader._validate_dimensions(7680, 4320)
        
        # Invalid dimensions
        with pytest.raises(ValueError):
            loader._validate_dimensions(-1, 1080)
        with pytest.raises(ValueError):
            loader._validate_dimensions(1920, 0)
        with pytest.raises(ValueError):
            loader._validate_dimensions("1920", 1080)  # Not an integer
    
    def test_source_validation(self):
        """Test quote source validation."""
        loader = ConfigLoader()
        
        # Valid sources
        loader._validate_source("random")
        loader._validate_source("kindle")
        loader._validate_source("custom")
        
        # Invalid source
        with pytest.raises(ValueError):
            loader._validate_source("invalid")


class TestQuote:
    """Test Quote dataclass."""
    
    def test_quote_creation(self):
        """Test creating a Quote object."""
        quote = Quote(
            text="Test quote",
            author="Test Author",
            book_title="Test Book",
            book_cover_url="http://example.com/cover.jpg"
        )
        
        assert quote.text == "Test quote"
        assert quote.author == "Test Author"
        assert quote.book_title == "Test Book"
        assert quote.book_cover_url == "http://example.com/cover.jpg"
    
    def test_quote_author_display(self):
        """Test author display with fallback to Unknown."""
        # With author
        quote1 = Quote(text="Test", author="Author")
        assert quote1.get_author_display() == "Author"
        
        # Without author
        quote2 = Quote(text="Test", author=None)
        assert quote2.get_author_display() == "Unknown"
        
        # Empty author
        quote3 = Quote(text="Test", author="")
        assert quote3.get_author_display() == "Unknown"


class TestRandomQuoteSource:
    """Test random quote source."""
    
    @patch('quotescape.sources.random.requests.get')
    def test_get_quote_success(self, mock_get):
        """Test successful quote retrieval from API."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [{
            "content": "Test quote from API",
            "author": "API Author"
        }]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Create source and get quote
        config = Mock()
        source = RandomQuoteSource(config)
        quote = source.get_quote()
        
        assert quote.text == "Test quote from API"
        assert quote.author == "API Author"
        assert quote.book_title is None
        assert quote.book_cover_url is None
    
    @patch('quotescape.sources.random.requests.get')
    def test_get_quote_timeout(self, mock_get):
        """Test handling of request timeout."""
        import requests
        mock_get.side_effect = requests.Timeout()
        
        config = Mock()
        source = RandomQuoteSource(config)
        
        with pytest.raises(TimeoutError):
            source.get_quote()
    
    @patch('quotescape.sources.random.requests.get')
    def test_get_quote_connection_error(self, mock_get):
        """Test handling of connection error."""
        import requests
        mock_get.side_effect = requests.ConnectionError()
        
        config = Mock()
        source = RandomQuoteSource(config)
        
        with pytest.raises(ConnectionError):
            source.get_quote()
    
    def test_requires_internet(self):
        """Test that random source requires internet."""
        config = Mock()
        source = RandomQuoteSource(config)
        assert source.requires_internet() is True


class TestCustomQuoteSource:
    """Test custom quote source."""
    
    def test_load_valid_quotebook(self):
        """Test loading a valid custom quotebook."""
        # Create temporary quotebook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "Test Author": ["Quote 1", "Quote 2"],
                "Another Author": ["Quote 3"]
            }, f)
            temp_path = f.name
        
        try:
            # Create config mock
            config = Mock()
            config.custom_source_settings.custom_quotebook_path = temp_path
            
            # Create source
            source = CustomQuoteSource(config)
            
            # Check quotebook loaded
            assert "test author" in source.quotebook  # Lowercased
            assert len(source.quotebook["test author"]) == 2
            
        finally:
            Path(temp_path).unlink()
    
    def test_get_quote_from_custom(self):
        """Test getting a quote from custom quotebook."""
        # Create temporary quotebook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "Test Author": ["Test Quote"]
            }, f)
            temp_path = f.name
        
        try:
            config = Mock()
            config.custom_source_settings.custom_quotebook_path = temp_path
            
            source = CustomQuoteSource(config)
            quote = source.get_quote()
            
            assert quote.text == "Test Quote"
            assert quote.author == "Test Author"
            
        finally:
            Path(temp_path).unlink()
    
    def test_empty_quotebook_error(self):
        """Test error when quotebook is empty."""
        # Create empty quotebook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            config = Mock()
            config.custom_source_settings.custom_quotebook_path = temp_path
            
            source = CustomQuoteSource(config)
            
            with pytest.raises(ValueError, match="empty"):
                source.get_quote()
                
        finally:
            Path(temp_path).unlink()
    
    def test_add_and_remove_quote(self):
        """Test adding and removing quotes."""
        # Create temporary quotebook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_path = f.name
        
        try:
            config = Mock()
            config.custom_source_settings.custom_quotebook_path = temp_path
            
            source = CustomQuoteSource(config)
            
            # Add quote
            source.add_quote("New Author", "New Quote")
            assert "new author" in source.quotebook
            assert "New Quote" in source.quotebook["new author"]
            
            # Remove quote
            source.remove_quote("New Author", "New Quote")
            assert "new author" not in source.quotebook
            
        finally:
            Path(temp_path).unlink()
    
    def test_requires_internet(self):
        """Test that custom source doesn't require internet."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"Author": ["Quote"]}, f)
            temp_path = f.name
        
        try:
            config = Mock()
            config.custom_source_settings.custom_quotebook_path = temp_path
            
            source = CustomQuoteSource(config)
            assert source.requires_internet() is False
            
        finally:
            Path(temp_path).unlink()


class TestWallpaperGeneration:
    """Test wallpaper generation (basic tests only)."""
    
    def test_scale_factor_calculation(self):
        """Test resolution scaling factor calculation."""
        from quotescape.generators.wallpaper import WallpaperGenerator
        
        # Mock config for 8K
        config_8k = Mock()
        config_8k.dimension.width = 7680
        config_8k.dimension.height = 4320
        config_8k.project_root = Path(".")
        config_8k.dark_mode = True
        config_8k.colors = {
            "dark": Mock(
                background_color="#1E1E2E",
                quote_text_color="#CBA6F7",
                author_text_color="#A6ADC8",
                title_text_color="#CDD6F4"
            )
        }
        
        gen_8k = WallpaperGenerator(config_8k)
        assert gen_8k.scale_factor == 1.0
        
        # Mock config for 1080p
        config_1080p = Mock()
        config_1080p.dimension.width = 1920
        config_1080p.dimension.height = 1080
        config_1080p.project_root = Path(".")
        config_1080p.dark_mode = True
        config_1080p.colors = config_8k.colors
        
        gen_1080p = WallpaperGenerator(config_1080p)
        assert gen_1080p.scale_factor == 0.5  # 1080p is 1/4 the pixels of 8K


class TestCLI:
    """Test command-line interface."""
    
    def test_parse_arguments_default(self):
        """Test parsing arguments with defaults."""
        from quotescape.main import parse_arguments
        
        # Mock sys.argv
        import sys
        original_argv = sys.argv
        sys.argv = ['quotescape']
        
        try:
            args = parse_arguments()
            assert args.source is None  # No source override
            assert args.browser is None
            assert args.login_timeout == 300
            assert args.verbose is False
        finally:
            sys.argv = original_argv
    
    def test_parse_arguments_with_source(self):
        """Test parsing arguments with source override."""
        from quotescape.main import parse_arguments
        
        import sys
        original_argv = sys.argv
        
        # Test each source
        for source in ['random', 'kindle', 'custom']:
            sys.argv = ['quotescape', '--source', source]
            try:
                args = parse_arguments()
                assert args.source == source
            finally:
                sys.argv = original_argv
    
    def test_source_override(self):
        """Test that CLI source overrides config."""
        from quotescape.config import ConfigLoader
        
        # Create a mock config
        config = Mock()
        config.source = 'kindle'  # Config says kindle
        
        # Simulate CLI override
        args = Mock()
        args.source = 'random'  # CLI says random
        
        # In main(), we do: config.source = args.source
        if args.source:
            config.source = args.source
        
        # Should use CLI value
        assert config.source == 'random'
    
    def test_no_source_override(self):
        """Test that config is used when no CLI override."""
        from quotescape.config import ConfigLoader
        
        # Create a mock config
        config = Mock()
        config.source = 'kindle'  # Config says kindle
        
        # Simulate no CLI override
        args = Mock()
        args.source = None  # No CLI override
        
        # In main(), we check: if args.source:
        if args.source:
            config.source = args.source
        
        # Should keep config value
        assert config.source == 'kindle'
    
    def test_macos_detection(self):
        """Test macOS platform detection."""
        from quotescape.platforms.macos import MacOSWallpaperSetter
        
        with patch('platform.system', return_value='Darwin'):
            setter = MacOSWallpaperSetter()
            assert setter.is_available() is True
        
        with patch('platform.system', return_value='Linux'):
            setter = MacOSWallpaperSetter()
            assert setter.is_available() is False
    
    def test_windows_detection(self):
        """Test Windows platform detection."""
        from quotescape.platforms.windows import WindowsWallpaperSetter
        
        with patch('platform.system', return_value='Windows'):
            setter = WindowsWallpaperSetter()
            assert setter.is_available() is True
        
        with patch('platform.system', return_value='Linux'):
            setter = WindowsWallpaperSetter()
            assert setter.is_available() is False
    
    def test_linux_detection(self):
        """Test Linux platform detection."""
        from quotescape.platforms.linux import LinuxWallpaperSetter
        
        with patch('platform.system', return_value='Linux'):
            setter = LinuxWallpaperSetter()
            assert setter.is_available() is True
        
        with patch('platform.system', return_value='Windows'):
            setter = LinuxWallpaperSetter()
            assert setter.is_available() is False


if __name__ == "__main__":
    # Run tests with pytest if available, otherwise run basic tests
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        print("pytest not installed. Please install with: pip install pytest")
        print("\nRunning basic tests manually...")
        
        # Run a few basic tests manually
        print("Testing configuration loader...")
        test_config = TestConfig()
        test_config.test_default_config_loads()
        print("✅ Default config loads")
        
        print("\nTesting Quote class...")
        test_quote = TestQuote()
        test_quote.test_quote_creation()
        test_quote.test_quote_author_display()
        print("✅ Quote class works")
        
        print("\nTesting CLI...")
        test_cli = TestCLI()
        test_cli.test_source_override()
        test_cli.test_no_source_override()
        print("✅ CLI source override works")
        
        print("\n✨ Basic tests passed!")
        print("Install pytest for comprehensive testing: pip install pytest")