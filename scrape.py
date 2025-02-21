import os
import re
import json
import argparse
import requests

# Base URLs
INDEX_URL = "https://reportcard.ospi.k12.wa.us/Home/Index"
IMAGE_URL = (
    "https://tableau.ospi.k12.wa.us/t/Public/views/"
    "ReportCard_TopButtons/LeftSide?iframeSizedToWindow=true"
    "&:embed=y&:showAppBanner=false&:display_count=no"
    "&:showVizHome=no&:format=png&:showVizHome=n"
    "&:tabs=n&:toolbar=n&organizationid={}"
)

# Data storage directories
DATA_DIR = os.path.join(os.getcwd(), "data")
HTML_PATH = os.path.join(DATA_DIR, "index_page.html")
SCHOOLS_JSON_PATH = os.path.join(DATA_DIR, "schools.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Timeout settings (in seconds)
REQUEST_TIMEOUT = 10  # Adjust as needed

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Extract school data and images from OSPI report card."
)
parser.add_argument(
    "districts", nargs="*", help="One or more district names. If none "
    "are provided, all schools will be processed."
)
parser.add_argument(
    "--elementary-only", action="store_true",
    help="Restrict to elementary schools only."
)
args = parser.parse_args()
selected_districts = set(args.districts)  # Convert to set for lookup

# Step 1: Download HTML if not already saved
if not os.path.exists(HTML_PATH):
    print("🌐 Downloading index page...")
    try:
        response = requests.get(INDEX_URL, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            with open(HTML_PATH, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Saved index HTML to {HTML_PATH}")
        else:
            print(f"❌ Failed to download index page. "
                  f"Status code: {response.status_code}")
            exit()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching index page: {e}")
        exit()

# Step 2: Load HTML content
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# Step 3: Extract school data using regex
school_pattern = re.findall(
    r'availableTags\.push\("(.+?), (.+?)"\);\s*'
    r'organizationIdArray\.push\((\d+)\);', html_content
)

# Convert extracted data into a structured dictionary
all_schools = [
    {"school_name": school, "district": district,
     "organization_id": int(org_id)}
    for school, district, org_id in school_pattern
]

# Step 4: Apply district filtering (if specified)
if selected_districts:
    print(f"🔍 Searching for schools in: {', '.join(selected_districts)}")
    filtered_schools = [
        school for school in all_schools
        if any(d in school["district"] for d in selected_districts)
    ]
else:
    print("🔍 No district specified. Processing all schools in Washington.")
    filtered_schools = all_schools

# Step 5: Apply elementary school filter if the flag is used
if args.elementary_only:
    filtered_schools = [
        school for school in filtered_schools
        if "Elementary" in school["school_name"]
    ]
    print(f"✅ Elementary schools only: {len(filtered_schools)} found.")

if not filtered_schools:
    print("⚠️ No schools found based on the given criteria. "
          "Check district names or filters.")
    exit()

print(f"✅ Extracted {len(filtered_schools)} schools.")

# Step 6: Save extracted data
with open(SCHOOLS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(filtered_schools, f, indent=4)

print(f"✅ School data saved to {SCHOOLS_JSON_PATH}")

# Step 7: Download images for the selected schools
for school in filtered_schools:
    org_id = school["organization_id"]
    image_url = IMAGE_URL.format(org_id)
    image_path = os.path.join(IMAGES_DIR, f"{org_id}.png")

    print(f"📥 Downloading image for {school['school_name']} "
          f"({school['district']}, ID: {org_id})...")

    # Download image if not already saved
    if not os.path.exists(image_path):
        try:
            response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    img_file.write(response.content)
                print(f"✅ Image saved: {image_path}")
            else:
                print(f"❌ Failed to download image for \
                      {school['school_name']}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error downloading image for \
                  {school['school_name']}: {e}")
    else:
        print(f"🟡 Image for {school['school_name']} already exists. Skipping.")

print("🎉 Done! Extracted data and downloaded images.")
