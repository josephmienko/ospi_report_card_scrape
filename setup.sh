#!/bin/bash

echo "🔧 Setting up dependencies for OSPI report card scraper on macOS..."

# Ensure Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "⚠️ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Python (if not installed)
if ! command -v python3 &> /dev/null; then
    echo "⚠️ Python3 not found. Installing Python..."
    brew install python
fi

# Install Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "⚠️ Tesseract not found. Installing Tesseract OCR..."
    brew install tesseract
fi

# Install required Python packages
pip install my_package-1.0.0-py3-none-any.whl

# Make Python scripts executable
chmod +x scrape.py
chmod +x extract.py

# Final message
echo "✅ Process complete. Check the file 'lake_washington_elementary_report_cards.csv' for results."
