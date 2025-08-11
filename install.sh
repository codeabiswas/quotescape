#!/usr/bin/env bash

# Quotescape Installation Script for macOS and Linux
# This script sets up Quotescape with all necessary dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║     Quotescape Installation Script   ║"
echo "║         Generate Quote Wallpapers    ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    print_error "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version is 3.11+
PYTHON_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    print_info "Please install Python 3.11 from https://python.org or using your package manager"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the Quotescape project root directory"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        $PYTHON -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    $PYTHON -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
print_info "Installing Python dependencies..."
if command -v uv &> /dev/null; then
    print_info "Using uv to install dependencies..."
    uv sync
else
    print_info "Using pip to install dependencies..."
    pip install -r requirements.txt --quiet
fi
print_success "Dependencies installed"

# Run setup script
print_info "Running setup script..."
python setup.py

# Platform-specific checks
print_info "Checking platform-specific requirements..."
OS_TYPE=$(uname -s)

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS
    print_info "Detected macOS"
    
elif [ "$OS_TYPE" = "Linux" ]; then
    # Linux
    print_info "Detected Linux"
    
    # Check for wallpaper setting tools
    if ! command -v gsettings &> /dev/null && \
       ! command -v qdbus &> /dev/null && \
       ! command -v feh &> /dev/null; then
        print_warning "No wallpaper setting tool found"
        echo "For automatic wallpaper setting, install one of:"
        echo "  - GNOME: gsettings (usually pre-installed)"
        echo "  - KDE: qdbus (usually pre-installed)"
        echo "  - Generic: feh (sudo apt install feh / sudo pacman -S feh)"
    fi
    
    # Check for browser drivers for Kindle scraping
    if ! command -v google-chrome &> /dev/null && \
       ! command -v firefox &> /dev/null && \
       ! command -v chromium &> /dev/null; then
        print_warning "No supported browser found for Kindle scraping"
        echo "To use Kindle highlights, install one of:"
        echo "  - Google Chrome"
        echo "  - Firefox"
        echo "  - Chromium"
    fi
fi

# Create example configuration files
print_info "Creating example configuration files..."

# Create example custom quotebook if it doesn't exist
if [ ! -f "custom_quotebook.json" ]; then
    cat > custom_quotebook.json << 'EOF'
{
  "Marcus Aurelius": [
    "You have power over your mind - not outside events. Realize this, and you will find strength."
  ],
  "Maya Angelou": [
    "I've learned that people will forget what you said, people will forget what you did, but people will never forget how you made them feel."
  ]
}
EOF
    print_success "Created example custom_quotebook.json"
fi

# Create example Kindle secrets template if it doesn't exist
if [ ! -f "kindle_secrets.json.template" ]; then
    cat > kindle_secrets.json.template << 'EOF'
{
  "username": "your_amazon_email@example.com",
  "password": "your_amazon_password"
}
EOF
    print_success "Created kindle_secrets.json.template"
fi

# Create convenience scripts
print_info "Creating convenience scripts..."

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate 2>/dev/null || true
python run_quotescape.py "$@"
EOF
chmod +x run.sh

# Create uninstall script
cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "Removing Quotescape installation..."
rm -rf venv
rm -rf src/output/wallpapers/*.png
rm -rf src/output/cache/*.json
rm -f run.sh
rm -f uninstall.sh
echo "✅ Quotescape uninstalled"
echo "Note: Configuration files were preserved"
EOF
chmod +x uninstall.sh

print_success "Convenience scripts created"

# Final summary
echo
echo -e "${GREEN}╔══════════════════════════════════════╗"
echo -e "║     Installation Complete! 🎉        ║"
echo -e "╚══════════════════════════════════════╝${NC}"
echo
echo "Quick Start:"
echo "-----------"
echo "1. Run with random quotes (default):"
echo "   ${BLUE}./run.sh${NC}"
echo
echo "2. Run with custom quotes:"
echo "   - Edit ${YELLOW}custom_quotebook.json${NC}"
echo "   - Run: ${BLUE}./run.sh${NC} (after setting source to 'custom' in config)"
echo
echo "3. Run with Kindle highlights:"
echo "   - Copy ${YELLOW}kindle_secrets.json.template${NC} to ${YELLOW}kindle_secrets.json${NC}"
echo "   - Add your Amazon credentials"
echo "   - Run: ${BLUE}./run.sh${NC} (after setting source to 'kindle' in config)"
echo
echo "Other Commands:"
echo "--------------"
echo "  ${BLUE}./run.sh --help${NC}          Show all options"
echo "  ${BLUE}./run.sh -v${NC}              Verbose mode"
echo "  ${BLUE}./uninstall.sh${NC}           Uninstall Quotescape"
echo "  ${BLUE}make help${NC}                Show all make commands"
echo
echo "Configuration:"
echo "-------------"
echo "Edit ${YELLOW}quotescape.yaml${NC} to customize settings"
echo "Default location: ${YELLOW}~/.config/quotescape/quotescape.yaml${NC}"
echo
print_info "Virtual environment activated. To deactivate, run: ${YELLOW}deactivate${NC}"