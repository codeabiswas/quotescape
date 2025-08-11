"""
Base class for platform-specific wallpaper setters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class WallpaperSetter(ABC):
    """Abstract base class for platform-specific wallpaper setters."""
    
    @abstractmethod
    def set_wallpaper(self, image_path: Path) -> Tuple[bool, str]:
        """
        Set the desktop wallpaper to the specified image.
        
        Args:
            image_path: Path to the wallpaper image file
            
        Returns:
            Tuple of (success, message)
            - success: True if wallpaper was set successfully
            - message: Success or error message
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this wallpaper setter is available on the current system.
        
        Returns:
            True if this setter can be used, False otherwise
        """
        pass
    
    def get_fallback_path(self, image_path: Path, config_dir: Path) -> Path:
        """
        Get fallback path for manual wallpaper setting.
        
        Args:
            image_path: Original image path
            config_dir: Configuration directory
            
        Returns:
            Path where wallpaper should be copied for manual access
        """
        fallback_dir = config_dir / "wallpaper"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        
        fallback_path = fallback_dir / image_path.name
        
        # Copy the file to fallback location
        import shutil
        shutil.copy2(image_path, fallback_path)
        
        return fallback_path