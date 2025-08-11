"""
Windows-specific wallpaper setter using ctypes.
"""

import platform
from pathlib import Path
from typing import Tuple
from .base import WallpaperSetter


class WindowsWallpaperSetter(WallpaperSetter):
    """Wallpaper setter for Windows using ctypes and Windows API."""
    
    def set_wallpaper(self, image_path: Path) -> Tuple[bool, str]:
        """
        Set wallpaper on Windows using ctypes.
        
        Args:
            image_path: Path to the wallpaper image
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import ctypes
            
            # Convert to absolute path
            abs_path = str(image_path.resolve())
            
            # Windows API constants
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 1
            SPIF_SENDCHANGE = 2
            
            # Set the wallpaper
            result = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            
            if result:
                return True, f"Wallpaper set successfully: {abs_path}"
            else:
                return False, "Failed to set wallpaper via Windows API"
                
        except ImportError:
            return False, "ctypes module not available (required for Windows)"
        except Exception as e:
            return False, f"Unexpected error setting wallpaper: {e}"
    
    def is_available(self) -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"