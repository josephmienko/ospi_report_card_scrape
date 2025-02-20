import time
import re
import cv2
import pytesseract
import requests
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize Selenium WebDriver (Headless Mode)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# OSPI Report Card URL
url = "https://reportcard.ospi.k12.wa.us/ReportCard"
driver.get(url)

# Wait for the district dropdown
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "districtChooser")))

# Select Lake Washington School District
district_dropdown = driver.find_element(By.ID, "districtChooser")
district_dropdown.send_keys("Lake Washington School District")

# Wait for school dropdown to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dropdownOrgPicker")))

# Extract all elementary school names and NCES codes
school_dropdown = driver.find_element(By.ID, "dropdownOrgPicker")
schools = []
for option in school_dropdown.find_elements(By.TAG_NAME, "option"):
    school_name = option.text.strip()
    nces_code = option.get_attribute("value")
    if "Elementary" in school_name:  # Only collect elementary schools
        schools.append((school_name, nces_code))

# Data storage
results = []

# Iterate through schools and scrape images
for school_name, nces_code in schools:
    print(f"Processing: {school_name} (NCES: {nces_code})")

    # Select the school
    school_dropdown.send_keys(school_name)
    time.sleep(2)  # Allow page load

    try:
        # Locate iframe containing the report card image
        iframe = driver.find_element(By.CSS_SELECTOR, "#ReportCard_Top_Button_Left iframe")
        iframe_src = iframe.get_attribute("src")

        # Download the image
        response = requests.get(iframe_src)
        image = Image.open(BytesIO(response.content))

        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess image for OCR
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((1, 1), np.uint8)
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(morphed, -1, sharpen_kernel)

        # OCR Processing
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.% "'
        extracted_text = pytesseract.image_to_string(sharpened, config=custom_config)

        # Extract numeric values
        percent_pattern = r"\d+\.\d%"
        matches = re.findall(percent_pattern, extracted_text)

        # Ensure 6 values are extracted
        if len(matches) == 6:
            foundational_ela = float(matches[3].replace("%", ""))
            foundational_math = float(matches[4].replace("%", ""))
            foundational_science = float(matches[5].replace("%", ""))
            college_ela = float(matches[0].replace("%", ""))
            college_math = float(matches[1].replace("%", ""))
            college_science = float(matches[2].replace("%", ""))
        else:
            print(f"⚠️ OCR issue at {school_name}, check manually.")
            foundational_ela = foundational_math = foundational_science = college_ela = college_math = college_science = None

        # Store in results list
        results.append({
            "School Name": school_name,
            "NCES Code": nces_code,
            "Foundational Grade-level Knowledge ELA": foundational_ela,
            "Foundational Grade-level Knowledge Math": foundational_math,
            "Foundational Grade-level Knowledge Science": foundational_science,
            "On Track to College ELA": college_ela,
            "On Track to College Math": college_math,
            "On Track to College Science": college_science,
        })

    except Exception as e:
        print(f"❌ Error processing {school_name}: {e}")

# Close the Selenium browser
driver.quit()

# Create Pandas DataFrame
df = pd.DataFrame(results)

# Save to CSV
csv_path = "lake_washington_elementary_report_cards.csv"
df.to_csv(csv_path, index=False)

print(f"\n✅ Data saved to {csv_path}")
