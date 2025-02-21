import re
import json
import cv2
import pytesseract
import numpy as np
import pandas as pd
from PIL import Image

# Load school data

DATA_DIR = os.path.join(os.getcwd(), "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "extracted_report_cards.csv")
SCHOOLS_JSON_PATH = os.path.join(DATA_DIR, "schools.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Load school list
with open(SCHOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    schools = json.load(f)

# Data storage
results = []

# Iterate through schools and process images
for school in schools:
    school_name = school["school_name"]
    org_id = school["organization_id"]
    image_path = f"{IMAGES_DIR}/{org_id}.png"

    print(f"📄 Processing: {school_name} (ID: {org_id})")

    try:
        # Load the image
        image = Image.open(image_path)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess image for OCR
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(
            gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC
        )
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        kernel = np.ones((1, 1), np.uint8)
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        sharpen_kernel = np.array(
            [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]
        )
        sharpened = cv2.filter2D(morphed, -1, sharpen_kernel)

        # OCR Processing
        custom_config = (
            r'--oem 3 --psm 6 -c tessedit_char_whitelist="'
            r'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            r'0123456789.%"'
        )
        extracted_text = pytesseract.image_to_string(
            sharpened, config=custom_config
        )

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
            foundational_ela = foundational_math = None
            foundational_science = college_ela = None
            college_math = college_science = None

        # Calculate new metrics
        performance_index = sum(
            filter(None, [
                foundational_ela, foundational_math, foundational_science,
                college_ela, college_math, college_science
            ])
        ) / 6

        grade_level_index = sum(
            filter(None, [
                foundational_ela, foundational_math, foundational_science
            ])
        ) / 3

        college_track_index = sum(
            filter(None, [college_ela, college_math, college_science])
        ) / 3

        # Store in results list
        results.append({
            "School Name": school_name,
            "Organization ID": org_id,
            "Foundational ELA": foundational_ela,
            "Foundational Math": foundational_math,
            "Foundational Science": foundational_science,
            "College Track ELA": college_ela,
            "College Track Math": college_math,
            "College Track Science": college_science,
            "Overall Performance Index": performance_index,
            "Grade Level Knowledge Index": grade_level_index,
            "College Track Index": college_track_index
        })

    except Exception as e:
        print(f"❌ Error processing {school_name}: {e}")

# Create Pandas DataFrame
df = pd.DataFrame(results)

# Rank calculations (Descending order: highest = 1, lowest = N)
rank_columns = [
    "Overall Performance Index", "Grade Level Knowledge Index",
    "College Track Index", "Foundational ELA", "Foundational Math",
    "Foundational Science", "College Track ELA", "College Track Math",
    "College Track Science"
]

for col in rank_columns:
    df[f"{col} Rank"] = df[col].rank(
        ascending=False, method="dense"
    ).astype(int)

# Save to CSV
df.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Data saved to {OUTPUT_CSV}")
