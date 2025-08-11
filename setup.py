#!/usr/bin/env python
"""
Setup script for Quotescape.
Downloads required fonts and creates necessary directories.
Requires Python 3.11 or higher.
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path
import shutil


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    if sys.version_info < (3, 11):
        print(f"❌ Error: Python 3.11 or higher is required (you have {sys.version})")
        print("Please install Python 3.11 from https://python.org")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def download_fonts():
    """Download and install B612 fonts from Google Fonts."""
    print("📥 Downloading B612 fonts...")
    
    # Create fonts directory
    fonts_dir = Path("assets/fonts")
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    # Google Fonts URL for B612
    font_url = "https://fonts.google.com/download?family=B612"
    zip_path = fonts_dir / "B612.zip"
    
    try:
        # Download font zip
        print("   Downloading from Google Fonts...")
        urllib.request.urlretrieve(font_url, zip_path)
        
        # Extract fonts
        print("   Extracting fonts...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract only the .ttf files we need
            for file in zip_ref.namelist():
                if file.endswith('.ttf') and 'static' not in file:
                    zip_ref.extract(file, fonts_dir)
                    
                    # Move to correct location
                    extracted_path = fonts_dir / file
                    if extracted_path.exists():
                        final_path = fonts_dir / extracted_path.name
                        shutil.move(str(extracted_path), str(final_path))
        
        # Clean up
        zip_path.unlink()
        
        # Remove any extracted directories
        for item in fonts_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
        
        print("✅ Fonts installed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading fonts: {e}")
        print("   Please download B612 fonts manually from: https://fonts.google.com/specimen/B612")
        return False


def create_directories():
    """Create necessary directory structure."""
    print("📁 Creating directory structure...")
    
    directories = [
        "src/output/wallpapers",
        "src/output/cache",
        "assets/fonts",
        "config",
        "examples"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {dir_path}")
    
    print("✅ Directories created successfully!")


def create_default_config():
    """Create default configuration file."""
    print("📝 Creating default configuration...")
    
    config_content = """# Quotescape Configuration
# Default configuration file

# Quote source: "random", "kindle", or "custom"
source: "random"

# Wallpaper dimensions (8K by default)
dimension:
  width: 7680
  height: 4320

# Dark mode
dark_mode: true

# Color configuration (Catppuccin themes)
colors:
  dark:
    background_color: "#1E1E2E"
    quote_text_color: "#CBA6F7"
    author_text_color: "#A6ADC8"
    title_text_color: "#CDD6F4"
  light:
    background_color: "#EFF1F5"
    quote_text_color: "#8839EF"
    author_text_color: "#6C6F85"
    title_text_color: "#4C4F69"

# Show author name
show_author: true

# Kindle-specific settings
kindle_source_settings:
  refresh_frequency: "monthly"
  show_book_cover: true
  show_book_title: true
  kindle_secrets_path: "config_directory"

# Custom quotes settings
custom_source_settings:
  custom_quotebook_path: "config_directory"
"""
    
    config_path = Path("config/quotescape.yaml")
    if not config_path.exists():
        config_path.write_text(config_content)
        print("✅ Default configuration created!")
    else:
        print("ℹ️  Configuration already exists, skipping...")


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    
    # Check if uv is available
    if shutil.which("uv"):
        print("   Using uv to install dependencies...")
        os.system("uv sync")
    else:
        print("   Using pip to install dependencies...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    print("✅ Dependencies installed!")


def main():
    """Run the complete setup process."""
    print("\n🎨 Quotescape Setup\n" + "="*50 + "\n")
    
    # Check Python version first
    check_python_version()
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Download fonts
    download_fonts()
    print()
    
    # Create default config
    create_default_config()
    print()
    
    # Install dependencies
    response = input("Do you want to install Python dependencies? (y/n): ")
    if response.lower() in ['y', 'yes']:
        install_dependencies()
    print()
    
    print("="*50)
    print("\n✨ Setup complete! You can now run Quotescape with:")
    print("   python run_quotescape.py")
    print("\nOr if using uv:")
    print("   uv run python run_quotescape.py")
    print("\nFor more options, run:")
    print("   python run_quotescape.py --help")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)