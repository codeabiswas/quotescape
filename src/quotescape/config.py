"""
Configuration handler for Quotescape.
Manages loading and validation of configuration from quotescape.yaml files.
"""

import os
import platform
import re
import yaml
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ColorConfig:
    """Color configuration for a theme (dark or light)."""
    background_color: str
    quote_text_color: str
    author_text_color: str
    title_text_color: str


@dataclass
class DimensionConfig:
    """Wallpaper dimension configuration."""
    width: int
    height: int


@dataclass
class KindleSettings:
    """Settings specific to Kindle source."""
    refresh_frequency: str
    show_book_cover: bool
    show_book_title: bool
    kindle_secrets_path: str


@dataclass
class CustomSettings:
    """Settings specific to Custom source."""
    custom_quotebook_path: str


@dataclass
class QuotescapeConfig:
    """Complete configuration for Quotescape application."""
    source: str
    dimension: DimensionConfig
    dark_mode: bool
    colors: Dict[str, ColorConfig]
    show_author: bool
    kindle_source_settings: KindleSettings
    custom_source_settings: CustomSettings
    
    # Runtime paths (not from config file)
    config_dir: Path = field(default_factory=Path)
    project_root: Path = field(default_factory=Path)


class ConfigLoader:
    """Handles loading and validation of Quotescape configuration."""
    
    # Valid options for various settings
    VALID_SOURCES = ["random", "kindle", "custom"]
    VALID_REFRESH_FREQUENCIES = ["always", "daily", "weekly", "monthly", "quarterly", "biannually", "annually"]
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "source": "random",
        "dimension": {
            "width": 7680,
            "height": 4320
        },
        "dark_mode": True,
        "colors": {
            "dark": {
                "background_color": "#1E1E2E",
                "quote_text_color": "#CBA6F7",
                "author_text_color": "#A6ADC8",
                "title_text_color": "#CDD6F4"
            },
            "light": {
                "background_color": "#EFF1F5",
                "quote_text_color": "#8839EF",
                "author_text_color": "#6C6F85",
                "title_text_color": "#4C4F69"
            }
        },
        "show_author": True,
        "kindle_source_settings": {
            "refresh_frequency": "monthly",
            "show_book_cover": True,
            "show_book_title": True,
            "kindle_secrets_path": "config_directory"
        },
        "custom_source_settings": {
            "custom_quotebook_path": "config_directory"
        }
    }
    
    def __init__(self):
        """Initialize the config loader."""
        self.project_root = self._find_project_root()
        self.config_path = None
        self.config_dir = None
        
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        # Start from the current file's location
        current = Path(__file__).resolve()
        
        # Look for markers that indicate project root
        markers = ['pyproject.toml', 'requirements.txt', '.git', 'config']
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
            
        # If not found, use current working directory
        return Path.cwd()
    
    def _get_config_search_paths(self) -> list[Path]:
        """Get the list of paths to search for config file based on platform."""
        paths = []
        system = platform.system()
        
        if system in ["Darwin", "Linux"]:  # macOS and Linux
            # XDG_CONFIG_HOME paths
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                paths.append(Path(xdg_config) / "quotescape" / "quotescape.yaml")
                paths.append(Path(xdg_config) / "quotescape.yaml")
            
            # Home directory paths
            home = Path.home()
            paths.append(home / ".config" / "quotescape" / "quotescape.yaml")
            paths.append(home / "quotescape.yaml")
            
            # System-wide path
            paths.append(Path("/etc") / "quotescape" / "quotescape.yaml")
            
        elif system == "Windows":
            # Windows APPDATA path
            appdata = os.environ.get("APPDATA")
            if appdata:
                paths.append(Path(appdata) / "quotescape" / "quotescape.yaml")
        
        # Add project's default config as fallback
        paths.append(self.project_root / "config" / "quotescape.yaml")
        
        return paths
    
    def _find_config_file(self) -> Optional[Path]:
        """Find the first existing config file in search paths."""
        search_paths = self._get_config_search_paths()
        
        for path in search_paths:
            if path.exists():
                return path
                
        return None
    
    def _validate_hex_color(self, color: str, field_name: str) -> None:
        """Validate that a color value is a valid hex color code."""
        pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        if not re.match(pattern, color):
            raise ValueError(f"Invalid hex color code for {field_name}: {color}")
    
    def _validate_dimensions(self, width: int, height: int) -> None:
        """Validate wallpaper dimensions."""
        if not isinstance(width, int) or width <= 0:
            raise ValueError(f"Width must be a positive integer, got: {width}")
        if not isinstance(height, int) or height <= 0:
            raise ValueError(f"Height must be a positive integer, got: {height}")
    
    def _validate_source(self, source: str) -> None:
        """Validate the quote source."""
        if source not in self.VALID_SOURCES:
            raise ValueError(
                f"Invalid source: {source}. Must be one of {self.VALID_SOURCES}"
            )
    
    def _validate_refresh_frequency(self, frequency: str) -> None:
        """Validate the refresh frequency for Kindle source."""
        if frequency not in self.VALID_REFRESH_FREQUENCIES:
            raise ValueError(
                f"Invalid refresh frequency: {frequency}. "
                f"Must be one of {self.VALID_REFRESH_FREQUENCIES}"
            )
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with default config."""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _resolve_paths(self, config: Dict) -> Dict:
        """Resolve special path values like 'config_directory'."""
        # Resolve kindle_secrets_path using match/case (Python 3.11+)
        kindle_path = config["kindle_source_settings"]["kindle_secrets_path"]
        match kindle_path:
            case "config_directory":
                config["kindle_source_settings"]["kindle_secrets_path"] = str(
                    self.config_dir / "kindle_secrets.json"
                )
            case _:
                config["kindle_source_settings"]["kindle_secrets_path"] = str(
                    Path(kindle_path).resolve()
                )
        
        # Resolve custom_quotebook_path
        custom_path = config["custom_source_settings"]["custom_quotebook_path"]
        match custom_path:
            case "config_directory":
                config["custom_source_settings"]["custom_quotebook_path"] = str(
                    self.config_dir / "custom_quotebook.json"
                )
            case _:
                config["custom_source_settings"]["custom_quotebook_path"] = str(
                    Path(custom_path).resolve()
                )
        
        return config
    
    def load(self) -> QuotescapeConfig:
        """Load and validate the configuration."""
        # Find config file
        self.config_path = self._find_config_file()
        
        if self.config_path:
            self.config_dir = self.config_path.parent
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error reading config file {self.config_path}: {e}")
                print("Using default configuration...")
                user_config = {}
        else:
            # Use default config location
            self.config_dir = self.project_root / "config"
            user_config = {}
            print("No config file found, using default configuration...")
        
        # Merge with defaults
        config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
        
        # Resolve special paths
        config = self._resolve_paths(config)
        
        # Validate configuration
        self._validate_source(config["source"])
        self._validate_dimensions(config["dimension"]["width"], config["dimension"]["height"])
        self._validate_refresh_frequency(config["kindle_source_settings"]["refresh_frequency"])
        
        # Validate colors
        for theme in ["dark", "light"]:
            for color_field, color_value in config["colors"][theme].items():
                self._validate_hex_color(color_value, f"{theme}.{color_field}")
        
        # Validate boolean values
        if not isinstance(config["dark_mode"], bool):
            raise ValueError("dark_mode must be true or false")
        if not isinstance(config["show_author"], bool):
            raise ValueError("show_author must be true or false")
        if not isinstance(config["kindle_source_settings"]["show_book_cover"], bool):
            raise ValueError("kindle_source_settings.show_book_cover must be true or false")
        if not isinstance(config["kindle_source_settings"]["show_book_title"], bool):
            raise ValueError("kindle_source_settings.show_book_title must be true or false")
        
        # Create config object
        return QuotescapeConfig(
            source=config["source"],
            dimension=DimensionConfig(
                width=config["dimension"]["width"],
                height=config["dimension"]["height"]
            ),
            dark_mode=config["dark_mode"],
            colors={
                "dark": ColorConfig(**config["colors"]["dark"]),
                "light": ColorConfig(**config["colors"]["light"])
            },
            show_author=config["show_author"],
            kindle_source_settings=KindleSettings(**config["kindle_source_settings"]),
            custom_source_settings=CustomSettings(**config["custom_source_settings"]),
            config_dir=self.config_dir,
            project_root=self.project_root
        )
    
    def get_active_colors(self, config: QuotescapeConfig) -> ColorConfig:
        """Get the active color configuration based on dark_mode setting."""
        return config.colors["dark"] if config.dark_mode else config.colors["light"]