![Project BRand](https://raw.githubusercontent.com/josephmienko/ospi_report_card_scrape/refs/heads/main/comparare.svg)


###### The `comparare` repository contains scripts and tools to gather information, match/bring-together that information, and summarize it to facilitate the comparison of one or more subjects of interest. At present, this simply contains Python scripts to facilitate comparison of schools on the basis of performance in reading, math, and science. My intention is to ultimately house those scraping tools and projects I've created throughout my career, and maintain them for by whoever might find them useful.  

## Overview
This repository contains two scripts:
1. `scrape.py` - Scrapes school data and report card images from OSPI.
2. `recognize.py` - Processes downloaded images using OCR to extract data.

## Installation and Usage

### 1. Setup and Run
Run the `setup.sh` script to set up dependencies and execute the entire workflow.

```bash
bash setup.sh [options]
```

### 2. Arguments
#### `scrape.py`
This script supports the following optional arguments:
- `--districts "District Name 1" "District Name 2"` (Fetch data for specific districts.)
- `--elementary_only` (Restrict output to elementary schools.)
- If no arguments are given, the script fetches all schools.

#### `ospi_report_card_ocr.py`
No additional arguments required. It processes images downloaded by the scraper. The --districts and --elementary_only arguments are nontheless available if you first obtain a larger set of data with `scrape.py`.

## Output
- Scraped school data is saved in `data/schools.json`.
- Extracted report card images are stored in `data/images/`.
- OCR results are compiled into `extracted_report_cards.csv`.

## Requirements
- Python 3
- Virtual environment (`venv`)
- Dependencies installed in `requirements.txt`

## Troubleshooting
If errors occur, try running:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Then re-run the scripts manually:
```bash
python3 scrape.py
python3 recognize.py
```
