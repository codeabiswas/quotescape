"""
Wallpaper generator for creating quote wallpapers.
Uses Pillow to generate beautiful wallpapers with quotes.
"""

import math
import random
import textwrap
import logging
import requests
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from ..sources.base import Quote
from ..config import QuotescapeConfig, ColorConfig


logger = logging.getLogger(__name__)


class WallpaperGenerator:
    """Generates wallpaper images from quotes."""
    
    # Default dimensions for scaling calculations
    DEFAULT_WIDTH = 7680
    DEFAULT_HEIGHT = 4320
    
    def __init__(self, config: QuotescapeConfig):
        """
        Initialize the wallpaper generator.
        
        Args:
            config: QuotescapeConfig object with all settings
        """
        self.config = config
        self.width = config.dimension.width
        self.height = config.dimension.height
        
        # Get color scheme based on dark mode setting
        self.colors = config.colors["dark"] if config.dark_mode else config.colors["light"]
        
        # Calculate scaling factor for fonts
        self.scale_factor = self._calculate_scale_factor()
        
        # Font paths
        self.project_root = config.project_root
        self.fonts_dir = self.project_root / "assets" / "fonts"
        
        # Ensure fonts directory exists
        if not self.fonts_dir.exists():
            # Try alternative location
            self.fonts_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
        
        # Load fonts
        self.quote_font = self._load_font("B612-Regular.ttf", self._scale_size(110))
        self.italic_font = self._load_font("B612-Italic.ttf", self._scale_size(60))
        
        # Output path
        self.output_dir = self.project_root / "src" / "output" / "wallpapers"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_scale_factor(self) -> float:
        """Calculate scaling factor based on resolution."""
        if self.width == self.DEFAULT_WIDTH and self.height == self.DEFAULT_HEIGHT:
            return 1.0
        
        current_pixels = self.width * self.height
        default_pixels = self.DEFAULT_WIDTH * self.DEFAULT_HEIGHT
        return math.sqrt(current_pixels / default_pixels)
    
    def _scale_size(self, size: int) -> int:
        """Scale a size value based on the current resolution."""
        return int(size * self.scale_factor)
    
    def _load_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """
        Load a font file.
        
        Args:
            font_name: Name of the font file
            size: Font size in pixels
            
        Returns:
            Loaded font object
            
        Raises:
            FileNotFoundError: If font file not found
        """
        font_path = self.fonts_dir / font_name
        
        if not font_path.exists():
            # Try to use a system font as fallback
            try:
                return ImageFont.truetype("Arial", size)
            except:
                logger.warning(f"Font {font_name} not found, using default font")
                return ImageFont.load_default()
        
        return ImageFont.truetype(str(font_path), size)
    
    def _download_image(self, url: str) -> Optional[Image.Image]:
        """
        Download an image from URL.
        
        Args:
            url: URL of the image
            
        Returns:
            PIL Image object or None if download fails
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return None
    
    def _get_default_cover(self) -> Image.Image:
        """
        Get default book cover image.
        
        Returns:
            Default book cover image
        """
        # Create a simple default cover
        cover = Image.new('RGBA', (600, 900), (100, 100, 100, 255))
        draw = ImageDraw.Draw(cover)
        
        # Add text to indicate it's a default cover
        text = "Book Cover"
        font = self._load_font("B612-Regular.ttf", 48)
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (600 - text_width) // 2
        y = (900 - text_height) // 2
        
        draw.text((x, y), text, fill=(200, 200, 200), font=font)
        
        return cover
    
    def generate(self, quote: Quote) -> Path:
        """
        Generate a wallpaper from a quote.
        
        Args:
            quote: Quote object containing text and metadata
            
        Returns:
            Path to the generated wallpaper file
        """
        # Create base image
        image = Image.new('RGB', (self.width, self.height), self.colors.background_color)
        draw = ImageDraw.Draw(image)
        
        # Determine layout based on source and settings
        if quote.book_cover_url and self.config.kindle_source_settings.show_book_cover:
            self._draw_kindle_layout(draw, image, quote)
        else:
            self._draw_simple_layout(draw, quote)
        
        # Generate unique filename
        filename = f"quotescape{random.randint(0, 9999):04d}.png"
        filepath = self.output_dir / filename
        
        # Delete old wallpapers
        self._cleanup_old_wallpapers()
        
        # Save the image
        image.save(filepath, 'PNG')
        logger.info(f"Generated wallpaper: {filepath}")
        
        return filepath
    
    def _draw_simple_layout(self, draw: ImageDraw.Draw, quote: Quote) -> None:
        """
        Draw simple layout for random/custom quotes.
        
        Layout:
        [Quote Text - Centered & Wrapped]
               [Author Name]
        """
        # Wrap quote text
        wrapper = textwrap.TextWrapper(width=100)
        lines = wrapper.wrap(quote.text)
        
        # Calculate total height needed
        quote_height = len(lines) * self._scale_size(110)
        author_height = self._scale_size(60) if self.config.show_author else 0
        spacing = self._scale_size(60) if self.config.show_author else 0
        total_height = quote_height + spacing + author_height
        
        # Calculate starting Y position
        y_start = (self.height - total_height) // 2
        
        # Find longest line for centering
        max_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.quote_font)
            line_width = bbox[2] - bbox[0]
            max_width = max(max_width, line_width)
        
        # Draw quote lines
        y = y_start
        x_start = (self.width - max_width) // 2
        
        for line in lines:
            draw.text(
                (x_start, y),
                line,
                fill=self.colors.quote_text_color,
                font=self.quote_font
            )
            y += self._scale_size(110)
        
        # Draw author if enabled
        if self.config.show_author:
            author_text = quote.get_author_display()
            draw.text(
                (x_start, y + self._scale_size(60)),
                author_text,
                fill=self.colors.author_text_color,
                font=self.italic_font
            )
    
    def _draw_kindle_layout(self, draw: ImageDraw.Draw, image: Image.Image, quote: Quote) -> None:
        """
        Draw Kindle layout with book cover.
        
        Layout:
        [Book Cover] | [Quote Text - Centered & Wrapped]
                     | [Book Title]
                     | [Author Name]
        """
        # Download or get book cover
        cover_image = None
        if quote.book_cover_url:
            cover_image = self._download_image(quote.book_cover_url)
        
        if not cover_image:
            cover_image = self._get_default_cover()
        
        # Convert and resize cover
        cover_image = cover_image.convert("RGBA")
        thumbnail_size = self._scale_size(2250)
        cover_image.thumbnail((thumbnail_size, thumbnail_size))
        cover_width, cover_height = cover_image.size
        
        # Wrap quote text (narrower due to cover)
        wrapper = textwrap.TextWrapper(width=60)
        lines = wrapper.wrap(quote.text)
        
        # Calculate heights
        quote_height = len(lines) * self._scale_size(110)
        title_height = self._scale_size(60) if self.config.kindle_source_settings.show_book_title and quote.book_title else 0
        author_height = self._scale_size(60) if self.config.show_author else 0
        spacing = self._scale_size(60)
        
        text_height = quote_height
        if title_height:
            text_height += spacing + title_height
        if author_height:
            text_height += spacing + author_height
        
        # Find longest quote line
        max_quote_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.quote_font)
            line_width = bbox[2] - bbox[0]
            max_quote_width = max(max_quote_width, line_width)
        
        # Calculate positions
        total_width = cover_width + self._scale_size(250) + max_quote_width
        x_start = (self.width - total_width) // 2
        
        # Draw book cover with shadow
        if self.config.dark_mode:
            shadow_color = "#11111B"
        else:
            shadow_color = "#DCE0E8"
        
        shadow_offset = self._scale_size(65)
        
        # Draw shadow
        draw.rectangle(
            [
                x_start + shadow_offset,
                (self.height - cover_height) // 2 + shadow_offset,
                x_start + cover_width + shadow_offset,
                (self.height + cover_height) // 2 + shadow_offset
            ],
            fill=shadow_color
        )
        
        # Paste book cover
        cover_position = (x_start, (self.height - cover_height) // 2)
        image.paste(cover_image, cover_position, cover_image)
        
        # Calculate text starting position
        text_x = x_start + cover_width + self._scale_size(250)
        text_y = (self.height - text_height) // 2
        
        # Draw quote lines
        y = text_y
        for line in lines:
            draw.text(
                (text_x, y),
                line,
                fill=self.colors.quote_text_color,
                font=self.quote_font
            )
            y += self._scale_size(110)
        
        # Draw book title if enabled
        if self.config.kindle_source_settings.show_book_title and quote.book_title:
            draw.text(
                (text_x, y + spacing),
                quote.book_title,
                fill=self.colors.title_text_color,
                font=self.italic_font
            )
            y += spacing + self._scale_size(60)
        
        # Draw author if enabled
        if self.config.show_author:
            author_text = quote.get_author_display()
            y_pos = y + spacing if not quote.book_title else y
            draw.text(
                (text_x, y_pos),
                author_text,
                fill=self.colors.author_text_color,
                font=self.italic_font
            )
    
    def _cleanup_old_wallpapers(self) -> None:
        """Delete old wallpaper files."""
        for file in self.output_dir.glob("quotescape*.png"):
            try:
                file.unlink()
            except Exception as e:
                logger.warning(f"Could not delete old wallpaper {file}: {e}")