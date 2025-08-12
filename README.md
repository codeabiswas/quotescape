# Quotescape 🎨

Generate beautiful quote wallpapers for your desktop. Quotescape creates inspiring wallpapers from random quotes, your Kindle highlights, or custom quotes you provide.

## Requirements

- **Python 3.11** (required for modern features and dependency compatibility)
- Internet connection (for random quotes and initial Kindle scraping)
- Supported operating system: macOS, Windows, or Linux

## Features

- **Three Quote Sources:**
  - 🎲 **Random**: Fetches quotes from The Quotes Hub API
  - 📚 **Kindle**: Uses your personal Kindle highlights
  - ✍️ **Custom**: Your own curated collection of quotes

- **Cross-Platform Support:**
  - 🍎 macOS
  - 🪟 Windows
  - 🐧 Linux (GNOME, KDE, XFCE, and more)

- **Beautiful Design:**
  - Catppuccin color schemes (Mocha for dark mode, Latte for light mode)
  - Dynamic font scaling for any resolution
  - Book covers displayed for Kindle quotes
  - Clean, minimalist aesthetic

## Installation

### Using Homebrew (Recommended for macOS/Linux users)

```bash
# Add the tap
brew tap codeabiswas/quotescape

# Install Quotescape
brew install quotescape

# Run Quotescape
quotescape --help
```

This will install Quotescape with all dependencies in an isolated environment. Configuration files will be stored in:
- Config: `/usr/local/etc/quotescape/`
- Wallpapers: `/usr/local/var/quotescape/wallpapers/`

### Manual Installation

#### Using uv (Recommended for development)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and run
uv sync
uv run python -m quotescape.main
```

#### Using pip

```bash
# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Quotescape
python -m quotescape.main
```

## Quick Start

### For Homebrew Installation

```bash
# Generate a random quote wallpaper
quotescape

# Use custom quotes
quotescape --source custom

# Use Kindle highlights
quotescape --source kindle
```

### For Manual Installation

#### Random Quote (Default)

```bash
# Using uv
uv run python -m quotescape.main

# Using pip
python -m quotescape.main
```

This will fetch a random quote from the internet and set it as your wallpaper.

#### Custom Quotes

1. Create a `quotescape.yaml` configuration file:
```yaml
source: "custom"
```

2. Create a `custom_quotebook.json` file:
```json
{
  "Yoda": [
    "Do or do not. There is no try.",
    "Fear is the path to the dark side."
  ],
  "Albert Einstein": [
    "Imagination is more important than knowledge.",
    "Life is like riding a bicycle. To keep your balance, you must keep moving."
  ]
}
```

3. Run Quotescape:
```bash
# Homebrew installation
quotescape

# Manual installation
python -m quotescape.main
```

#### Kindle Highlights

1. Create a `quotescape.yaml` configuration file:
```yaml
source: "kindle"
```

2. Create a `kindle_secrets.json` file with your Amazon credentials:
```json
{
  "username": "your_email@example.com",
  "password": "your_password"
}
```

3. Run Quotescape:
```bash
# Homebrew installation
quotescape

# Manual installation
python -m quotescape.main
```

**Note**: On first run, Quotescape will open a browser to scrape your Kindle highlights. If 2FA is enabled, you'll need to complete the verification in the browser.

## Configuration

Quotescape looks for configuration files in the following locations (in order):

#### macOS and Linux
1. `$XDG_CONFIG_HOME/quotescape/quotescape.yaml`
2. `$XDG_CONFIG_HOME/quotescape.yaml`
3. `$HOME/.config/quotescape/quotescape.yaml`
4. `$HOME/quotescape.yaml`
5. `/etc/quotescape/quotescape.yaml`

#### Windows
1. `%APPDATA%\quotescape\quotescape.yaml`

**Note:** To use Kindle or Custom sources, you must first create a `quotescape.yaml` configuration file and populate it with something in one of the supported directories. This file is required because it tells Quotescape (1) which source to use and (2) where to find your other configuration files. Once created, place your `kindle_secrets.json` and/or `custom_quotebook.json` files in the same directory as your `quotescape.yaml` file. Without this configuration file, these additional files cannot be located, even if they exist.

### Configuration Options

```yaml
# Quote source: "random", "kindle", or "custom"
source: "random"

# Wallpaper dimensions
dimension:
  width: 7680   # Width in pixels
  height: 4320  # Height in pixels

# Dark mode
dark_mode: true

# Color configuration
colors:
  dark:
    background_color: "#1E1E2E"  # Catppuccin Mocha Base
    quote_text_color: "#CBA6F7"  # Catppuccin Mocha Mauve
    author_text_color: "#A6ADC8" # Catppuccin Mocha Subtext0
    title_text_color: "#CDD6F4"  # Catppuccin Mocha Text
  light:
    background_color: "#EFF1F5"  # Catppuccin Latte Base
    quote_text_color: "#8839EF"  # Catppuccin Latte Mauve
    author_text_color: "#6C6F85" # Catppuccin Latte Subtext0
    title_text_color: "#4C4F69"  # Catppuccin Latte Text

# Show author name
show_author: true

# Kindle-specific settings
kindle_source_settings:
  # Refresh frequency options:
  # - "always": Refresh every run (never use cache)
  # - "daily": Refresh once per day
  # - "weekly": Refresh once per week  
  # - "monthly": Refresh once per month (default)
  # - "quarterly": Refresh every 3 months
  # - "biannually": Refresh every 6 months
  # - "annually": Refresh once per year
  refresh_frequency: "monthly"
  show_book_cover: true         # Display book cover
  show_book_title: true         # Display book title
  kindle_secrets_path: "config_directory"  # Path to kindle_secrets.json

# Custom quotes settings
custom_source_settings:
  custom_quotebook_path: "config_directory"  # Path to custom_quotebook.json
```

### CLI Flags

- **`--browser <edge, chrome, safari, firefox>`** - Force specific browser for Kindle scraping
- **`--login-timeout <positive_integer>`** - Seconds to wait for login completion before timeout (default is 300)
- **`--source <random, kindle, custom>`** - Use specified source for quote
- **`--refresh-kindle`** - Force refresh the Kindle quotebook cache regardless of refresh frequency
- **`-v, --verbose`** - Enable detailed logging during Kindle login and scraping
- **`-h, --help`** - Display help information, version, and available flags

## Examples

### Set a random quote wallpaper
```bash
# Homebrew installation
quotescape

# Manual installation
python -m quotescape.main
```

### Override source via CLI (ignores config file)
```bash
# Use random quotes regardless of config
quotescape --source random  # Homebrew
python -m quotescape.main --source random  # Manual

# Use Kindle highlights
quotescape --source kindle  # Homebrew
python -m quotescape.main --source kindle  # Manual

# Use custom quotes
quotescape --source custom  # Homebrew
python -m quotescape.main --source custom  # Manual
```

### Use Kindle highlights with Chrome browser
```bash
# Homebrew installation
quotescape --source kindle --browser chrome

# Manual installation
python -m quotescape.main --source kindle --browser chrome
```

### Enable verbose logging for debugging
```bash
# Homebrew installation
quotescape -v

# Manual installation
python -m quotescape.main -v
```

### Extend login timeout for slow connections
```bash
# Homebrew installation
quotescape --source kindle --login-timeout 600

# Manual installation
python -m quotescape.main --source kindle --login-timeout 600
```

## Project Structure

```
quotescape/
├── src/
│   ├── quotescape/          # Main package
│   │   ├── config.py        # Configuration handling
│   │   ├── main.py          # Entry point
│   │   ├── sources/         # Quote sources
│   │   ├── scrapers/        # Web scrapers
│   │   ├── generators/      # Image generation
│   │   └── platforms/       # Platform-specific code
│   └── output/
│       ├── wallpapers/      # Generated wallpapers
│       └── cache/           # Cached data
├── assets/
│   └── fonts/               # B612 font files
├── config/
│   └── quotescape.yaml      # Default configuration
├── pyproject.toml           # uv package configuration
├── requirements.txt         # pip dependencies
└── README.md
```

## Troubleshooting

### Installation Issues

#### Homebrew Installation
- **Formula not found**: Make sure you've added the tap: `brew tap codeabiswas/quotescape`
- **Python version mismatch**: Homebrew will install Python 3.11 automatically
- **Permission issues**: Try `brew reinstall quotescape`

#### Manual Installation
- **Python Version Issues**:
  - Install Python 3.11 from [python.org](https://python.org) or using your package manager
  - For uv: Make sure you're using Python 3.11 exactly (`python --version`)
  - pyenv users: Run `pyenv local 3.11` in the project directory

### Browser Issues (Kindle)
- **Chrome/Edge/Firefox not found**: Install the browser or use `--browser` to specify an available one
- **Safari on macOS**: Enable "Developer > Allow Remote Automation" in Safari preferences

### 2FA/Login Issues (Kindle)
- When prompted, complete 2FA in the browser window that opens
- Use `--login-timeout` to extend the wait time if needed
- Make sure your `kindle_secrets.json` has correct credentials

### Wallpaper Not Setting Automatically
- **Linux**: Install `feh` or `nitrogen` for better compatibility
- **All platforms**: Check the output for the wallpaper location and set it manually if needed

### Font Issues
- Ensure the B612 font files are in the `assets/fonts/` directory
- The application will fall back to system fonts if B612 is not found

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/codeabiswas/quotescape.git
cd quotescape

# Using uv (recommended for development)
uv sync
uv run python -m quotescape.main

# Using pip
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m quotescape.main
```

### Running Tests

```bash
# With uv
uv run pytest

# With pip
python -m pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Credits

- Quotes API: [The Quotes Hub](https://thequoteshub.com)
- Font: [B612](https://fonts.google.com/specimen/B612) by Airbus
- Color Schemes: [Catppuccin](https://github.com/catppuccin/catppuccin)

## Future Features

- Recent quote avoidance
- Dynamic color matching using AI
- Mobile app (Android/iOS)
- GUI with system tray integration

## Support

If you encounter any issues or have questions:
- Check the [Troubleshooting](#troubleshooting) section
- Open an issue on [GitHub](https://github.com/codeabiswas/quotescape/issues)
- Check existing issues for similar problems

## Changelog (To be used in future iterations)

See CHANGELOG.md for a list of changes in each version.

---

Made with ❤️ by [Andrei Biswas](https://github.com/codeabiswas)