import os
import csv
import requests
from urllib.parse import urlparse
from pathlib import Path
import pandas as pd

# File paths
input_csv = "IndianFoodDatasetCSV.csv"
output_folder = "images"
output_csv = "image_labels.csv"

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file
df = pd.read_csv(input_csv)

# Optional: Adjust column names if needed
image_column = 'URL'
label_column = 'RecipeName'  # or use 'TranslatedRecipeName' if preferred

# New rows for the output CSV
image_mappings = []
existing_files = set(os.listdir(output_folder))

for idx, row in df.iterrows():
    url = row[image_column]
    label = row[label_column]

    # Build the filename
    filename = f"{idx}_{Path(urlparse(url).path).name}"
    image_path = os.path.join(output_folder, filename)

    # ✅ Check if this file already exists
    if filename in existing_files:
        print(f"Already downloaded: {filename}")
        image_mappings.append((filename, label))
        continue

    try:
        # Get and save the image
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            image_mappings.append((filename, label))
        else:
            print(f"Failed to download: {url}")
    except Exception as e:
        print(f"Error with {url}: {e}")

# Save mapping CSV
with open(output_csv, "w", newline="", encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "label"])
    writer.writerows(image_mappings)

print(f"\n✅ Done! Images saved in '{output_folder}' and CSV saved as '{output_csv}'.")
