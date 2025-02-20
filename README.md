# ospi_report_card_scrape

This repo contains a python script to gather data to compare elementary schools within a Washington State School District. 

## How the Script (`ospi_report_card_scrape.py`) Works

✅ Scrapes report cards all elementary schools in Lake Washington School District.

✅ Extracts Tableau generated images dynamically from the OSPI Report Card site.

✅ Uses OpenCV preprocessing for better OCR accuracy.

✅ Extracts six performance metrics per school: The percent of students at the school with Foundational Grade-level Knowledge in English Language Arts (ELA), Math, and Science and the percent of children at the school on track to complete college coursework in ELA, Math, or Science. 

✅ Saves the results in a structured CSV file

## What The Setup Script (`setup_and_run.sh`) Does (for a Mac)

✅ Installs all required dependencies (Python, Tesseract, Chrome, ChromeDriver).

✅ Sets up the OSPI scraping script automatically.

✅ Runs the scraper and saves data to lake_washington_elementary_report_cards.csv.

✅ Handles errors & dependencies automatically.
