from datasets import load_dataset

dataset = load_dataset("rajistics/indian_food_images")
train_ds = dataset["train"]

print(train_ds.features)  # This should print available labels
