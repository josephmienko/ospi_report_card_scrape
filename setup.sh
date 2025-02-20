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

# Install required Python packages
echo "📦 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install selenium pillow pytesseract opencv-python numpy pandas requests

# Install Tesseract OCR
if ! command -v tesseract &> /dev/null; then
    echo "⚠️ Tesseract not found. Installing Tesseract OCR..."
    brew install tesseract
fi

# Install Google Chrome
if ! command -v google-chrome &> /dev/null; then
    echo "⚠️ Google Chrome not found. Installing Chrome..."
    brew install --cask google-chrome
fi

# Install ChromeDriver (match Chrome version)
echo "🔄 Installing ChromeDriver..."
brew install chromedriver

# Make Python script executable
chmod +x ospi_report_card_scrape.py

# Run the scraper
echo "🚀 Running OSPI scraper..."
python3 ospi_report_card_scrape.py

# Final message
echo "✅ Process complete. Check the file 'lake_washington_elementary_report_cards.csv' for results."
