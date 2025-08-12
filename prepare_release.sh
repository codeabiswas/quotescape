#!/usr/bin/env bash

# Quotescape Homebrew Release Preparation Script
# This script helps prepare a new release for Homebrew distribution

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_USER="codeabiswas"
MAIN_REPO="quotescape"
TAP_REPO="homebrew-quotescape"

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   Quotescape Homebrew Release Preparer   ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists git; then
    print_error "git is not installed"
    exit 1
fi

if ! command_exists curl; then
    print_error "curl is not installed"
    exit 1
fi

if ! command_exists shasum; then
    print_error "shasum is not installed"
    exit 1
fi

print_success "All prerequisites met"

# Get version
current_version=$(grep '__version__' src/quotescape/main.py | cut -d'"' -f2)
print_info "Current version in main.py: $current_version"

echo
read -p "Enter the new version number (without 'v' prefix, e.g., 1.0.1): " new_version

if [[ ! "$new_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Please use semantic versioning (e.g., 1.0.1)"
    exit 1
fi

# Update version in source files
print_info "Updating version in source files..."

# Update main.py
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/quotescape/main.py && rm src/quotescape/main.py.bak
print_success "Updated src/quotescape/main.py"

# Update pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml && rm pyproject.toml.bak
print_success "Updated pyproject.toml"

# Commit version changes
print_info "Committing version changes..."
git add src/quotescape/main.py pyproject.toml
git commit -m "Bump version to $new_version" || {
    print_warning "No changes to commit (version might already be updated)"
}

# Create and push tag
print_info "Creating git tag v$new_version..."
git tag -a "v$new_version" -m "Release version $new_version"

echo
read -p "Push tag to GitHub? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin "v$new_version"
    print_success "Tag pushed to GitHub"
else
    print_warning "Tag not pushed. Run 'git push origin v$new_version' when ready"
fi

# Wait for GitHub to process
print_info "Waiting for GitHub to process the tag..."
sleep 3

# Download tarball and calculate SHA256
print_info "Downloading release tarball..."
tarball_url="https://github.com/$GITHUB_USER/$MAIN_REPO/archive/refs/tags/v$new_version.tar.gz"
tarball_file="./tmp/quotescape-$new_version.tar.gz"

curl -L "$tarball_url" -o "$tarball_file" 2>/dev/null || {
    print_error "Failed to download tarball. Make sure the tag is pushed to GitHub"
    exit 1
}

print_success "Downloaded tarball"

# Calculate SHA256
print_info "Calculating SHA256..."
sha256=$(shasum -a 256 "$tarball_file" | cut -d' ' -f1)
print_success "SHA256: $sha256"

# Generate updated formula
print_info "Generating updated formula..."

formula_file="quotescape.rb"
temp_formula="./tmp/quotescape.rb"

# Check if we have the formula template
if [ ! -f "$formula_file" ]; then
    print_warning "Formula file not found. Creating from template..."
    # The formula should already exist from the artifact above
    print_error "Please ensure quotescape.rb exists in the current directory"
    exit 1
fi

# Update formula with new version and SHA256
sed "s|archive/refs/tags/v.*\.tar\.gz|archive/refs/tags/v$new_version.tar.gz|g" "$formula_file" > "$temp_formula"
sed -i.bak "s|sha256 \".*\"|sha256 \"$sha256\"|g" "$temp_formula" && rm "$temp_formula.bak"

print_success "Formula updated"

# Show the diff
print_info "Formula changes:"
echo "----------------------------------------"
diff "$formula_file" "$temp_formula" || true
echo "----------------------------------------"

echo
read -p "Apply these changes to the formula? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mv "$temp_formula" "$formula_file"
    print_success "Formula updated with new version and SHA256"
else
    print_warning "Formula not updated. Temporary formula saved at $temp_formula"
fi

# Create release notes
print_info "Generating release notes template..."

release_notes_file="./tmp/release_notes_v$new_version.md"
cat > "$release_notes_file" << EOF
# Quotescape v$new_version

## What's Changed
<!-- Add your changes here -->
- 

## Installation

### Homebrew (macOS/Linux)
\`\`\`bash
brew tap $GITHUB_USER/$TAP_REPO
brew install quotescape
\`\`\`

### Manual Installation
\`\`\`bash
git clone https://github.com/$GITHUB_USER/$MAIN_REPO.git
cd quotescape
python -m pip install -r requirements.txt
python run_quotescape.py
\`\`\`

## SHA256 Checksum
\`$sha256\`

---
**Full Changelog**: https://github.com/$GITHUB_USER/$MAIN_REPO/compare/v$current_version...v$new_version
EOF

print_success "Release notes template created at $release_notes_file"

# Summary
echo
echo -e "${GREEN}╔══════════════════════════════════════════╗"
echo -e "║           Release Prepared! 🎉           ║"
echo -e "╚══════════════════════════════════════════╝${NC}"
echo
echo "Next steps:"
echo "1. ${BLUE}Create GitHub Release:${NC}"
echo "   - Go to: https://github.com/$GITHUB_USER/$MAIN_REPO/releases/new"
echo "   - Select tag: v$new_version"
echo "   - Title: Quotescape v$new_version"
echo "   - Copy release notes from: $release_notes_file"
echo "   - Publish release"
echo
echo "2. ${BLUE}Update Homebrew Tap:${NC}"
echo "   - Copy $formula_file to your tap repository"
echo "   - Commit and push to: https://github.com/$GITHUB_USER/$TAP_REPO"
echo
echo "3. ${BLUE}Test Installation:${NC}"
echo "   \$ brew tap $GITHUB_USER/$TAP_REPO"
echo "   \$ brew install quotescape"
echo "   \$ quotescape --version"
echo
echo "Version: ${GREEN}$new_version${NC}"
echo "SHA256:  ${GREEN}$sha256${NC}"

# Cleanup
rm -f "$tarball_file"

print_success "Release preparation complete!"