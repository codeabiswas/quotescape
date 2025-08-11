"""
Linux-specific wallpaper setter with desktop environment detection.
Supports GNOME, KDE, XFCE, and generic X11 environments.
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Tuple, Optional
from .base import WallpaperSetter


class LinuxWallpaperSetter(WallpaperSetter):
    """Wallpaper setter for Linux with DE auto-detection."""
    
    def __init__(self):
        """Initialize and detect desktop environment."""
        self.desktop_env = self._detect_desktop_environment()
    
    def _detect_desktop_environment(self) -> Optional[str]:
        """
        Detect the current desktop environment.
        
        Returns:
            Name of desktop environment or None if unknown
        """
        # Check environment variables
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()
        
        # Combine both for easier checking
        env_hints = f"{desktop} {session}"
        
        # Use match/case for cleaner detection (Python 3.11+)
        for de_name in ["gnome", "kde", "plasma", "xfce", "mate", 
                        "cinnamon", "lxde", "lxqt", "unity"]:
            if de_name in env_hints:
                match de_name:
                    case "plasma":
                        return "kde"
                    case _:
                        return de_name
        
        # Check if running under X11
        if os.environ.get("DISPLAY"):
            return "x11"
        
        return None
    
    def set_wallpaper(self, image_path: Path) -> Tuple[bool, str]:
        """
        Set wallpaper on Linux based on detected desktop environment.
        
        Args:
            image_path: Path to the wallpaper image
            
        Returns:
            Tuple of (success, message)
        """
        abs_path = str(image_path.resolve())
        
        if not self.desktop_env:
            return False, (
                "Unable to detect desktop environment. "
                "Please set the wallpaper manually using your system settings."
            )
        
        # Use match/case for cleaner dispatching (Python 3.11+)
        match self.desktop_env:
            case "gnome":
                return self._set_gnome_wallpaper(abs_path)
            case "kde":
                return self._set_kde_wallpaper(abs_path)
            case "xfce":
                return self._set_xfce_wallpaper(abs_path)
            case "mate":
                return self._set_mate_wallpaper(abs_path)
            case "cinnamon":
                return self._set_cinnamon_wallpaper(abs_path)
            case "lxde":
                return self._set_lxde_wallpaper(abs_path)
            case "lxqt":
                return self._set_lxqt_wallpaper(abs_path)
            case "unity":
                return self._set_unity_wallpaper(abs_path)
            case "x11":
                return self._set_x11_wallpaper(abs_path)
            case _:
                return False, f"Unsupported desktop environment: {self.desktop_env}"
    
    def _set_gnome_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for GNOME using gsettings."""
        try:
            # Convert to file URI
            file_uri = f"file://{path}"
            
            # Set for both light and dark themes
            commands = [
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", file_uri],
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", file_uri]
            ]
            
            for cmd in commands:
                subprocess.run(cmd, check=True, capture_output=True)
            
            return True, f"Wallpaper set successfully for GNOME: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set GNOME wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting GNOME wallpaper: {e}"
    
    def _set_kde_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for KDE Plasma using qdbus."""
        try:
            script = f"""
            qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
                var allDesktops = desktops();
                for (i=0;i<allDesktops.length;i++) {{
                    d = allDesktops[i];
                    d.wallpaperPlugin = "org.kde.image";
                    d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                    d.writeConfig("Image", "file://{path}")
                }}
            '
            """
            subprocess.run(script, shell=True, check=True, capture_output=True)
            return True, f"Wallpaper set successfully for KDE: {path}"
        except subprocess.CalledProcessError:
            # Try alternative method
            try:
                subprocess.run(
                    ["plasma-apply-wallpaperimage", path],
                    check=True,
                    capture_output=True
                )
                return True, f"Wallpaper set successfully for KDE: {path}"
            except:
                return False, "Failed to set KDE wallpaper"
        except Exception as e:
            return False, f"Unexpected error setting KDE wallpaper: {e}"
    
    def _set_xfce_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for XFCE using xfconf-query."""
        try:
            # Get all monitors
            result = subprocess.run(
                ["xfconf-query", "-c", "xfce4-desktop", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Set wallpaper for each monitor
            for line in result.stdout.splitlines():
                if "/last-image" in line or "/image-path" in line:
                    subprocess.run(
                        ["xfconf-query", "-c", "xfce4-desktop", "-p", line, "-s", path],
                        check=True,
                        capture_output=True
                    )
            
            return True, f"Wallpaper set successfully for XFCE: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set XFCE wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting XFCE wallpaper: {e}"
    
    def _set_mate_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for MATE using gsettings."""
        try:
            subprocess.run(
                ["gsettings", "set", "org.mate.background", "picture-filename", path],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully for MATE: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set MATE wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting MATE wallpaper: {e}"
    
    def _set_cinnamon_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for Cinnamon using gsettings."""
        try:
            file_uri = f"file://{path}"
            subprocess.run(
                ["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", file_uri],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully for Cinnamon: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set Cinnamon wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting Cinnamon wallpaper: {e}"
    
    def _set_lxde_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for LXDE using pcmanfm."""
        try:
            subprocess.run(
                ["pcmanfm", "--set-wallpaper", path],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully for LXDE: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set LXDE wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting LXDE wallpaper: {e}"
    
    def _set_lxqt_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for LXQt using pcmanfm-qt."""
        try:
            subprocess.run(
                ["pcmanfm-qt", "--set-wallpaper", path],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully for LXQt: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set LXQt wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting LXQt wallpaper: {e}"
    
    def _set_unity_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for Unity using gsettings."""
        try:
            file_uri = f"file://{path}"
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", file_uri],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully for Unity: {path}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set Unity wallpaper: {e}"
        except Exception as e:
            return False, f"Unexpected error setting Unity wallpaper: {e}"
    
    def _set_x11_wallpaper(self, path: str) -> Tuple[bool, str]:
        """Set wallpaper for generic X11 using feh."""
        try:
            # Try feh first
            subprocess.run(
                ["feh", "--bg-fill", path],
                check=True,
                capture_output=True
            )
            return True, f"Wallpaper set successfully using feh: {path}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Try nitrogen
            try:
                subprocess.run(
                    ["nitrogen", "--set-auto", path],
                    check=True,
                    capture_output=True
                )
                return True, f"Wallpaper set successfully using nitrogen: {path}"
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False, (
                    "Unable to set wallpaper. Please install 'feh' or 'nitrogen', "
                    "or set the wallpaper manually."
                )
        except Exception as e:
            return False, f"Unexpected error setting X11 wallpaper: {e}"
    
    def is_available(self) -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"