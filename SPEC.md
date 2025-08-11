# Quotescape - Functional Specification

> **Last Updated:** 08/11/25

> **Started:** 08/10/25

## What?

An app that generates quote wallpapers and sets them as your desktop background. The quote can be random (from the Quotable API), a quote provided by you, or one of your Kindle highlights.

## Why?

- Once I highlight a good quote from one of my books, I will forget it. This is a way not to!
- A wallpaper that is simple yet dynamic and motivating is really cool

## MVP Requirements

### Core Technical Stack

- **Cross-platform:** macOS, Linux, and Windows
- **Fully Python development**
- **Package Management:** Development using `uv` (i.e., `uv sync` and `uv run <point_of_entry>.py`), but must also work the usual way (i.e., using `pip` and `python <point_of_entry>.py`)
- **Both `pyproject.toml` and `requirements.txt` will be provided**

### Supported Quote Sources

1. **Random** (from Quotable API) - default option
2. **Kindle** (scrapes highlighted quotes from Kindle Notebook)
3. **Custom** (user-added quotes)

### Platform-specific Installation Avenues

**macOS**

- Local artifact
- Homebrew (via custom tap)

**Linux**

- Local artifact
- Support using `gsettings` (GNOME), `qdbus` (KDE), or `feh`
- Auto-detects desktop environment
- If unsupported, notifies user to set the generated wallpaper manually

**Windows**

- Local artifact

## E2E Experience with Quote Sources

### Random (default option)

**Prerequisites**

- Requires internet connection to get quote from Quotable API

**Happy Flow**

- Install quotescape → Run `quotescape`
- Retrieves random quote from Quotable API (no filtering, uses whatever API returns)
- Generates wallpaper with quote
- Sets as desktop background

**Unhappy Flow**

- If no internet connection or error retrieving quote: Exit gracefully with helpful message explaining the issue

### Kindle

**Prerequisites**

- Requires internet connection to scrape quotes first time and when refresh is triggered
- Requires `kindle_secrets.json` file with Amazon credentials:

```json
{
   "username": "<amazon username>",
   "password": "<amazon password>"
}
```

**Happy Flow**

- Install quotescape → Create `quotescape.yaml` → Set `source: kindle` → Create `kindle_secrets.json` → Run `quotescape`
- **First time:** Scrapes Kindle highlights, saves to `kindle_quotebook.json`, selects random quote, sets wallpaper
- **Subsequent times:** Randomly selects from cached quotes collection and sets wallpaper
- **Refresh time:** Re-scrapes based on refresh frequency setting

**Refresh Mechanism**

- Checks `kindle_quotebook.json` last modified date on every run
- Compares against configured refresh frequency
- Re-scrapes if refresh period has elapsed
- **Default:** Monthly (1st of every month)
- **Options:** daily, weekly, monthly, quarterly, biannually, annually

**Unhappy Flow**

- No internet connection or scraping error: Exit with helpful message explaining issue
- Missing or malformed `kindle_secrets.json`: Inform user of specific issue and exit gracefully

**Web Scraping Implementation**

- Uses Selenium with BeautifulSoup for parsing
- No Kindle API exists, so scraping is necessary
- Handles Amazon 2FA:
    - Displays console message asking user to complete 2FA in browser
    - Waits for user to complete authentication
    - Timeout period configurable via `--login-timeout` flag (default timeout period is 300s)
    - If page after login is not expected, exits gracefully with explanation
- Browser priority order:
    - Uses system default browser if supported
    - Falls back in order: Chrome → Edge → Firefox → Safari (macOS only)
    - **Note:** If Safari is used, user must enable "Developer > Allow Remote Automation" setting
- Scrapes book covers from Amazon pages during the process

**kindle_quotebook.json Structure**

```json
{
    "<title of the book>\nBy: <author-name>": [
        "<book cover picture URL scraped from Amazon>",
        [
            "quote1",
            "quote2",
            "quote3"
        ]
    ]
}
```

### Custom

**Prerequisites**

- Requires populated `custom_quotebook.json` file with correct structure:

```json
{
    "author1": [
        "quote1",
        "quote2"
    ],
    "author2": [
        "quote1",
        "quote2"
    ]
}
```

**Happy Flow**

- Install quotescape → Create `quotescape.yaml` → Set `source: custom` → Create `custom_quotebook.json` → Run `quotescape`
- Randomly selects quote from custom collection
- Generates wallpaper and sets as background

**Unhappy Flow**

- Missing or malformed `custom_quotebook.json`: Inform user of issue when running quotescape

## Configuration

### Configuration File: `quotescape.yaml`

The app ships with a default configuration file. Users can create their own to override settings.

**Search Path Priority (stops at first found):**

**macOS and Linux:**

1. `$XDG_CONFIG_HOME/quotescape/quotescape.yaml`
2. `$XDG_CONFIG_HOME/quotescape.yaml`
3. `$HOME/.config/quotescape/quotescape.yaml`
4. `$HOME/quotescape.yaml`
5. `/etc/quotescape/quotescape.yaml`

**Windows:**

1. `%APPDATA%\quotescape\quotescape.yaml`

**Default Configuration:**

```yaml
# Quote source for wallpaper. Default: "random" 
# Options: "kindle", "random", "custom"
source: "random"

# Wallpaper dimensions. Default: 8K (7680x4320)
dimension:
  # Width (in px). Default: 7680
  width: 7680
  # Height (in px). Default: 4320
  height: 4320

# Dark mode. Default: true
dark_mode: true

# Color configuration for wallpaper
# Default (dark mode): Catppuccin Mocha
# Default (light mode): Catppuccin Latte
colors:
  dark:
    # Background color. Default: #1E1E2E
    background_color: "#1E1E2E"
    # Quote text color. Default: #CBA6F7
    quote_text_color: "#CBA6F7"
    # Author text color. Default: #A6ADC8
    author_text_color: "#A6ADC8"
    # Book title color (Kindle only). Default: #CDD6F4
    title_text_color: "#CDD6F4"
  light:
    # Background color. Default: #EFF1F5
    background_color: "#EFF1F5"
    # Quote text color. Default: #8839EF
    quote_text_color: "#8839EF"
    # Author text color. Default: #6C6F85
    author_text_color: "#6C6F85"
    # Book title color (Kindle only). Default: #4C4F69
    title_text_color: "#4C4F69"

# Show quote's author. Default: true
show_author: true

# Settings specific to Kindle source
kindle_source_settings:
  # Refresh frequency for highlights. Default: monthly
  # Options: daily, weekly, monthly, quarterly, biannually, annually
  refresh_frequency: "monthly"
  # Show book cover. Default: true
  # Falls back to default cover if retrieval fails
  show_book_cover: true
  # Show book title. Default: true
  show_book_title: true
  # Path to kindle_secrets.json. Default: same directory as config file
  kindle_secrets_path: "config_directory"

# Settings specific to Custom source
custom_source_settings:
  # Path to custom_quotebook.json. Default: same directory as config file
  custom_quotebook_path: "config_directory"
```

### Configuration Rules

1. **Hierarchy must be maintained** when overriding nested values
2. **Boolean values** must be exactly `true` or `false` (empty values cause error)
3. **Dimensions** must be positive integers for both width and height
4. **Source** must be exactly `random`, `custom`, or `kindle` (invalid values cause error)
5. **Color values** must be valid hex strings (e.g., "#1E1E2E")
6. **Paths** must be valid and contain appropriate files (invalid paths cause error with helpful message)
7. **refresh_frequency** must be one of the valid options (invalid values cause error)

## CLI Interface

### Main Command

```Bash
quotescape
```

### CLI Flags

- **`--browser <edge, chrome, safari, firefox>`** - Force specific browser for Kindle scraping
- **`--login-timeout <positive_integer>`** - Seconds to wait for login completion before timeout (default is 300)
- **`--source <random, kindle, custom>`** - Use specified source for quote
- **`-v, --verbose`** - Enable detailed logging during Kindle login and scraping
- **`-h, --help`** - Display help information, version, and available flags

## Image Generation

### Technical Implementation

- **Library:** Pillow (PIL)
- **Font:** B612 (bundled from Google Fonts)
- **Text wrapping:** Automatic for long quotes
- **Font scaling:** Dynamic sizing based on quote length

### Visual Layout

**For Random/Custom sources:**

```other
[Quote Text - Centered & Wrapped]
        [Author Name]
```

**For Kindle source:**

```other
[Book Cover] | [Quote Text - Centered & Wrapped]
             | [Book Title]
             | [Author Name]
```

All elements are centered as a group. Book cover appears to the left of the text block.

### File Management

- **Wallpaper location:** `<project_root>/src/output/wallpapers/quotescape<XXXX>.png`
    - XXXX = random 4-digit number
    - Previous wallpaper is deleted and replaced
- **Kindle cache:** `<project_root>/src/output/cache/kindle_quotebook.json`

## Platform-Specific Wallpaper Setting

### macOS

- Uses `osascript` to set desktop wallpaper

### Windows

- Uses `ctypes` with Windows API calls:

```python
ctypes.windll.user32.SystemParametersInfoW(20, 0, "path/to/wallpaper.png", 3)
```

### Linux

- Auto-detects desktop environment
- Attempts in order: `gsettings` (GNOME), `qdbus` (KDE), `feh` (fallback)

### Fallback Behavior (All Platforms)

- If automatic wallpaper setting fails on any platform:
    - Image is still saved to the default location: `<project_root>/src/output/wallpapers/quotescape<XXXX>.png`
    - Additionally saves a copy to `<config_directory>/wallpaper/quotescape<XXXX>.png` for easy access
    - Notifies user of the saved location so they can set it manually

## Error Handling

All errors result in:

1. Graceful exit
2. Clear, helpful error message explaining the issue
3. Suggestions for resolution where applicable
4. If wallpaper generation succeeds but setting fails:
    - Image is saved to default location: `<project_root>/src/output/wallpapers/quotescape<XXXX>.png`
    - Additional copy saved to `<config_directory>/wallpaper/quotescape<XXXX>.png` for easy manual access
    - User is notified of `<config_directory>/wallpaper/quotescape<XXXX>.png` location for manual setting

## Project Structure

```other
quotescape/
├── src/
│   ├── quotescape/
│   │   ├── __init__.py
│   │   ├── main.py           # Entry point
│   │   ├── config.py         # Config file handling
│   │   ├── scrapers/         # Kindle scraping logic
│   │   ├── generators/       # Image generation
│   │   ├── sources/          # Quote sources (quotable, kindle, custom)
│   │   └── platforms/        # OS-specific wallpaper setting
│   └── output/               # Runtime generated files
│       ├── wallpapers/       # Generated wallpaper images
│       └── cache/            # kindle_quotebook.json stored here
├── assets/
│   └── fonts/
│       └── B612-*.ttf        # Bundled B612 font files
├── config/
│   └── quotescape.yaml       # Default config shipped with app
├── pyproject.toml            # For uv package manager
├── requirements.txt          # For pip compatibility
└── README.md
```

## Special Considerations

### Anonymous Quotes

- For quotes without attribution, author is displayed as "Unknown"

### Quote Selection

- Pure random selection from available quotes
- No history tracking or recent quote avoidance

### Dependencies

- Must work with both `uv` and traditional `pip` installation methods
- All fonts are bundled with the application

## Future Features (Not in MVP)

- Recent quote avoidance
- Dynamic color matching using AI to match quote vibe
- Mobile app development (Android/iOS)
- GUI implementation (menubar/taskbar items)