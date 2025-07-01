from PIL import Image
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification

# 1️⃣ Load the model and processor
model_name = "prithivMLmods/Indian-Western-Food-34"
processor = AutoImageProcessor.from_pretrained(model_name)
model = SiglipForImageClassification.from_pretrained(model_name)
labels = model.config.id2label
for idx, label in labels.items():
    print(f"{idx}: {label}")
# 2️⃣ Load your test image
img = Image.open(r"C:\Users\Nayina\Downloads\ai_meal_planner\ai_meal_planner\app\dosai.jpg").convert("RGB")

# 3️⃣ Preprocess & predict
inputs = processor(images=img, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)
logits = outputs.logits
probs = torch.nn.functional.softmax(logits, dim=1).squeeze()

# 4️⃣ Map integer labels
predictions = {
    model.config.id2label[i]: float(probs[i]) for i in range(len(probs))
}

# 5️⃣ Show top 3
top3 = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]
print("\nTop 3 Predictions for the image:\n")
for label, score in top3:
    print(f"{label}: {score:.3f}")

