"""
macOS-specific wallpaper setter using osascript.
"""

import subprocess
import platform
from pathlib import Path
from typing import Tuple
from .base import WallpaperSetter


class MacOSWallpaperSetter(WallpaperSetter):
    """Wallpaper setter for macOS using osascript."""
    
    def set_wallpaper(self, image_path: Path) -> Tuple[bool, str]:
        """
        Set wallpaper on macOS using osascript.
        
        Args:
            image_path: Path to the wallpaper image
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Convert to absolute path
            abs_path = image_path.resolve()
            
            # AppleScript to set wallpaper
            script = f'''
            tell application "System Events"
                tell every desktop
                    set picture to "{abs_path}"
                end tell
            end tell
            '''
            
            # Run the AppleScript
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Refresh the Dock to apply changes
            subprocess.run(["killall", "Dock"], capture_output=True)
            
            return True, f"Wallpaper set successfully: {abs_path}"
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to set wallpaper via osascript: {e.stderr}"
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error setting wallpaper: {e}"
    
    def is_available(self) -> bool:
        """Check if running on macOS."""
        return platform.system() == "Darwin"