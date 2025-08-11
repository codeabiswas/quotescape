"""
Quotescape - Generate beautiful quote wallpapers for your desktop.

Main entry point for the Quotescape application.
"""

import sys
import platform
import argparse
import logging
from pathlib import Path
from typing import Optional

from .config import ConfigLoader, QuotescapeConfig
from .sources.base import QuoteSource
from .sources.random import RandomQuoteSource
from .sources.custom import CustomQuoteSource
from .sources.kindle import KindleQuoteSource
from .generators.wallpaper import WallpaperGenerator
from .platforms.base import WallpaperSetter
from .platforms.macos import MacOSWallpaperSetter
from .platforms.windows import WindowsWallpaperSetter
from .platforms.linux import LinuxWallpaperSetter


# Version information
__version__ = "1.0.0"


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        verbose: Enable verbose logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" if verbose else "%(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_quote_source(config: QuotescapeConfig, args: argparse.Namespace) -> QuoteSource:
    """
    Get the appropriate quote source based on configuration.
    
    Args:
        config: Quotescape configuration
        args: Command line arguments
        
    Returns:
        Configured quote source instance
        
    Raises:
        SystemExit: If source is not available
    """
    source_map = {
        "random": RandomQuoteSource,
        "custom": CustomQuoteSource,
        "kindle": lambda cfg: KindleQuoteSource(
            cfg,
            browser_name=args.browser,
            login_timeout=args.login_timeout,
            verbose=args.verbose
        )
    }
    
    if config.source not in source_map:
        print(f"Error: Unknown quote source: {config.source}", file=sys.stderr)
        sys.exit(1)
    
    # Create source instance
    if config.source == "kindle":
        source = source_map[config.source](config)
    else:
        source = source_map[config.source](config)
    
    # Check if source is available
    is_available, error_msg = source.is_available()
    if not is_available:
        print(f"Error: {config.source} source is not available: {error_msg}", file=sys.stderr)
        sys.exit(1)
    
    return source


def get_wallpaper_setter() -> WallpaperSetter:
    """
    Get the appropriate wallpaper setter for the current platform.
    
    Returns:
        Platform-specific wallpaper setter instance
        
    Raises:
        SystemExit: If platform is not supported
    """
    system = platform.system()
    
    # Use match/case for cleaner platform selection (Python 3.11+)
    match system:
        case "Darwin":
            setter = MacOSWallpaperSetter()
        case "Windows":
            setter = WindowsWallpaperSetter()
        case "Linux":
            setter = LinuxWallpaperSetter()
        case _:
            print(f"Error: Unsupported platform: {system}", file=sys.stderr)
            sys.exit(1)
    
    if not setter.is_available():
        print(f"Error: Wallpaper setter not available for {system}", file=sys.stderr)
        sys.exit(1)
    
    return setter


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="quotescape",
        description="Generate beautiful quote wallpapers for your desktop",
        epilog=f"Quotescape v{__version__} - Create inspiring wallpapers from quotes"
    )
    
    # Source override
    parser.add_argument(
        "--source",
        choices=["random", "kindle", "custom"],
        help="Override quote source from config (random, kindle, or custom)"
    )
    
    # Browser selection for Kindle scraping
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox", "edge", "safari"],
        help="Force specific browser for Kindle scraping"
    )
    
    # Login timeout for Kindle
    parser.add_argument(
        "--login-timeout",
        type=int,
        default=300,
        help="Seconds to wait for login completion (default: 300)"
    )
    
    # Verbose logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"Quotescape v{__version__}"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for Quotescape."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config_loader = ConfigLoader()
        config = config_loader.load()
        
        # Override source if specified via CLI
        if args.source:
            logger.info(f"Overriding source from config ('{config.source}') with CLI argument ('{args.source}')")
            config.source = args.source
        
        logger.info(f"Using quote source: {config.source}")
        logger.info(f"Resolution: {config.dimension.width}x{config.dimension.height}")
        logger.info(f"Dark mode: {config.dark_mode}")
        
        # Get quote source
        logger.info("Initializing quote source...")
        quote_source = get_quote_source(config, args)
        
        # Check if internet is required
        if quote_source.requires_internet():
            logger.info("This source requires internet connection")
        
        # Get a quote
        logger.info("Getting quote...")
        quote = quote_source.get_quote()
        
        logger.info(f"Quote: \"{quote.text[:50]}...\"")
        if quote.author:
            logger.info(f"Author: {quote.author}")
        if quote.book_title:
            logger.info(f"Book: {quote.book_title}")
        
        # Generate wallpaper
        logger.info("Generating wallpaper...")
        generator = WallpaperGenerator(config)
        wallpaper_path = generator.generate(quote)
        
        logger.info(f"Wallpaper generated: {wallpaper_path}")
        
        # Set wallpaper
        logger.info("Setting wallpaper...")
        setter = get_wallpaper_setter()
        success, message = setter.set_wallpaper(wallpaper_path)
        
        if success:
            print(f"\n✅ {message}")
            print(f"📍 Wallpaper location: {wallpaper_path}")
        else:
            # Try fallback
            logger.warning(f"Automatic wallpaper setting failed: {message}")
            
            fallback_path = setter.get_fallback_path(wallpaper_path, config.config_dir)
            print(f"\n⚠️  {message}")
            print(f"📍 Wallpaper saved to: {wallpaper_path}")
            print(f"📍 Also copied to: {fallback_path}")
            print("\nPlease set the wallpaper manually using your system settings.")
        
        print("\n🎨 Quotescape completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()