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

### Using pip

```bash
pip install -r requirements.txt
```

### Using uv (recommended)

```bash
uv sync
```

## Quick Start

### Random Quote (Default)

```bash
# Using pip
python -m quotescape.main

# Using uv
uv run python -m quotescape.main
```

This will fetch a random quote from the internet and set it as your wallpaper.

### Custom Quotes

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
python -m quotescape.main
```

### Kindle Highlights

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
python -m quotescape.main
```

**Note**: On first run, Quotescape will open a browser to scrape your Kindle highlights. If 2FA is enabled, you'll need to complete the verification in the browser.

## Configuration

Quotescape looks for configuration files in the following locations (in order):

### macOS and Linux
1. `$XDG_CONFIG_HOME/quotescape/quotescape.yaml`
2. `$XDG_CONFIG_HOME/quotescape.yaml`
3. `$HOME/.config/quotescape/quotescape.yaml`
4. `$HOME/quotescape.yaml`
5. `/etc/quotescape/quotescape.yaml`

### Windows
1. `%APPDATA%\quotescape\quotescape.yaml`

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
  refresh_frequency: "monthly"  # How often to refresh highlights
  show_book_cover: true         # Display book cover
  show_book_title: true         # Display book title
  kindle_secrets_path: "config_directory"  # Path to kindle_secrets.json

# Custom quotes settings
custom_source_settings:
  custom_quotebook_path: "config_directory"  # Path to custom_quotebook.json
```

## Command Line Options

```bash
quotescape [options]

Options:
  --browser {chrome,firefox,edge,safari}  Force specific browser for Kindle scraping
  --login-timeout SECONDS                  Timeout for login (default: 300)
  -v, --verbose                           Enable verbose logging
  --version                               Show version information
  -h, --help                              Show help message
```

## Examples

### Set a random quote wallpaper
```bash
python -m quotescape.main
```

### Use Kindle highlights with Chrome browser
```bash
python -m quotescape.main --browser chrome
```

### Enable verbose logging for debugging
```bash
python -m quotescape.main -v
```

### Extend login timeout for slow connections
```bash
python -m quotescape.main --login-timeout 600
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

### Python Version Issues
- **Error: "Python 3.11 or higher is required"**: Install Python 3.11 from [python.org](https://python.org) or using your package manager
- **uv dependency errors**: Make sure you're using Python 3.11 exactly (`python --version`)
- **pyenv users**: Run `pyenv local 3.11` in the project directory

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

### Running with uv
```bash
uv sync                    # Install dependencies
uv run python -m quotescape.main  # Run the application
```

### Running with pip
```bash
pip install -r requirements.txt
python -m quotescape.main
```

### Running tests
```bash
uv run pytest              # With uv
python -m pytest           # With pip
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Credits

- Quotes API: [The Quotes Hub](https://thequoteshub.com)
- Font: [B612](https://fonts.google.com/specimen/B612) by Airbus
- Color Schemes: [Catppuccin](https://github.com/catppuccin/catppuccin)

## Future Features

- Recent quote avoidance
- Dynamic color matching using AI
- Mobile app (Android/iOS)
- GUI with system tray integration