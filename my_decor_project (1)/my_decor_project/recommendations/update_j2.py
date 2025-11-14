import json
import os

# Define the correct image folder path
IMAGE_FOLDER = "static/images"

# Define mapping of styles to image filenames
style_images = {
    
    "Industrial": "industrial.jpeg",  # Added Industrial
    "Scandinavian": "scandinavian.jpeg"  # Added Scandinavian
}

# Load quiz data
json_file = "quiz_data.json"
with open(json_file, "r", encoding="utf-8") as file:
    quiz_data = json.load(file)

# Add image paths based on "Style Suggestion"
for item in quiz_data:
    style = item.get("Style Suggestion", "").strip()
    if style in style_images:
        # Correct file path format for JSON & URLs
        item["image"] = os.path.join(IMAGE_FOLDER, style_images[style]).replace("\\", "/")
    else:
        print(f"⚠ Warning: No image found for style '{style}'")  # Debugging message

# Print first 3 modified entries to verify
print("🔍 First 3 Entries After Modification:")
print(json.dumps(quiz_data[:3], indent=4))

# Save the updated JSON file
updated_json_file = "quiz_data.json"
with open(updated_json_file, "w", encoding="utf-8") as file:
    json.dump(quiz_data, file, indent=4)

print(f"✅ {updated_json_file} UPDATED Successfully with correct image paths! 🎉")
