# src/quotescape/platforms/__init__.py
"""Platform-specific wallpaper setters for Quotescape."""

from .base import WallpaperSetter
from .macos import MacOSWallpaperSetter
from .windows import WindowsWallpaperSetter
from .linux import LinuxWallpaperSetter

__all__ = [
    "WallpaperSetter",
    "MacOSWallpaperSetter",
    "WindowsWallpaperSetter",
    "LinuxWallpaperSetter"
]