from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import torch

# 1️⃣ Load the model & feature extractor
model_name = "DrishtiSharma/finetuned-SwinT-Indian-Food-Classification-v2"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

# 2️⃣ Load your test image
img = Image.open(r"C:\Users\Nayina\Downloads\ai_meal_planner\ai_meal_planner\app\idiyappam.jpg").convert("RGB")  # Replace with your path

# 3️⃣ Preprocess the image
inputs = feature_extractor(img, return_tensors="pt")

# 4️⃣ Get prediction
with torch.no_grad():
    outputs = model(**inputs)

# 5️⃣ Get the label
predicted_class = torch.argmax(outputs.logits, dim=-1).item()
label_name = model.config.id2label[predicted_class]

# ✅ Done!
print(f"Predicted Dish: {label_name}")

# Optional: Print all labels
#print(model.config.id2label)
