import pandas as pd

recipes = [
    {"id": 1, "name": "Peanut Butter Oats", "ingredients": "oats milk peanut butter", "diet": ["vegetarian"], "calories": 350},
    {"id": 2, "name": "Chicken Rice Bowl", "ingredients": "chicken rice broccoli", "diet": ["high-protein"], "calories": 500},
    {"id": 3, "name": "Banana Toast", "ingredients": "bread banana honey", "diet": ["vegetarian"], "calories": 300}
]

recipes_df = pd.DataFrame(recipes)
