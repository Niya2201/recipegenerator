from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import re
import torch
import io
import json
import httpx
import os
from typing import List
from pydantic import BaseModel
from app.recommender import recommend_meals
from app.substitution import replace_allergens
from app.calories import estimate_calories
from .recipe_db import recipes
from transformers import AutoImageProcessor, SiglipForImageClassification

# =================================================
# APP INIT
# =================================================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# UTILITY FUNCTIONS
# =================================================
def normalize_string(s: str) -> str:
    """Removes special chars and lowercases."""
    return re.sub(r'[^a-z0-9]', '', s.lower())

def search_recipes(dish_name: str):
    """Search for recipes by name in the dataset."""
    dish_query = normalize_string(dish_name)
    matched_results = {}

    for name, recipe_data in recipes.items():
        if dish_query in normalize_string(name):
            calories = estimate_calories(recipe_data.get("ingredients", []))
            recipe_copy = recipe_data.copy()
            recipe_copy["estimated_calories"] = calories
            matched_results[name] = recipe_copy

    return matched_results

def fetch_recipes(label_name: str):
    """Fetch matching recipes for predicted label."""
    dish_query = normalize_string(label_name)
    matching_recipes = []
    for dish_name, recipe_data in recipes.items():
        if dish_query in normalize_string(dish_name):
            calories = estimate_calories(recipe_data.get("ingredients", []))
            recipe_copy = recipe_data.copy()
            recipe_copy["estimated_calories"] = calories
            matching_recipes.append({
                "name": dish_name,
                "recipe": recipe_copy
            })
    return matching_recipes if matching_recipes else [{"error": "No recipe found for this prediction"}]

# =================================================
# MODEL INIT
# =================================================
MODEL_NAME = "prithivMLmods/Indian-Western-Food-34"
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = SiglipForImageClassification.from_pretrained(MODEL_NAME)

# =================================================
# ENDPOINTS
# =================================================
@app.post("/suggest_meals")
def suggest(data: dict):  # Should use MealRequest
    meals = recommend_meals(data["preferences"], data["allergies"], data["calories_per_meal"])
    if not meals:
        raise HTTPException(status_code=404, detail="No suitable meals found.")
    return {"meals": meals}

@app.post("/replace_allergens")
def substitute(data: dict):  # Should use AllergenInput
    return {"safe_ingredients": replace_allergens(data["ingredients"], data["allergies"])}

@app.post("/nutrition_info")
def mock_nutrition(data: dict):  # Should use NutritionInput
    return {
        "total_calories": len(data["ingredients"]) * 100,
        "ingredients": [{"name": i, "calories": 100} for i in data["ingredients"]]
    }

@app.post("/estimate_calories")
def estimate(data: dict):  # Should use CalorieEstimateInput
    calories = estimate_calories(data["ingredients"])
    return {"estimated_calories": calories}

@app.post("/recipe")
def get_recipe(data: dict):  # Should use DishRequest
    # print("hello testing inside get_recipe")
    matched_results = search_recipes(data["dish_name"])
    if not matched_results:
        raise HTTPException(status_code=404, detail="No recipes found for this dish.")
    # print("results",matched_results)
    return {"results": matched_results}

@app.post("/predict_and_recipe/")
async def predict_and_recipe(image_file: UploadFile = File(...)):
    """Predict the dish from an image and return matching recipes."""
    image_data = await image_file.read()
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    inputs = processor(images=img, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
    predictions = {
        model.config.id2label[i]: float(probs[i]) for i in range(len(probs))
    }
    top_label = max(predictions.items(), key=lambda x: x[1])[0]
    matched_results = search_recipes(top_label)

    if not matched_results:
        raise HTTPException(status_code=404, detail=f"No recipes found for predicted dish: {top_label}")

    return {"predicted_label": top_label, "results": matched_results}

@app.post("/user_profile")
def user_profile(data: dict):  # Should use UserProfileInput
    height_in_m = data["height"] / 100.0
    bmi = data["weight"] / (height_in_m ** 2)

    bmr = 10 * data["weight"] + 6.25 * data["height"] - 5 * data["age"] + 5
    activity_multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
    multiplier = activity_multipliers.get(data["activity_level"].lower(), 1.2)

    daily_calorie_target = round(bmr * multiplier)

    return {
        "bmi": round(bmi, 2),
        "daily_calorie_target": daily_calorie_target,
        "allergies": data["allergies"]
    }

# =================================================
# Substitution Endpoints
# =================================================
with open(r"C:\Users\Nayina\Downloads\ai_meal_planner\ai_meal_planner\app\substitution.json") as f:
    substitutions = json.load(f)

@app.post("/ingredient_substitution_bulk")
def get_substitution(data: dict):  # Should use SubstitutionRequest
    results = {}
    for allergen in data["allergies"]:
        results[allergen] = substitutions.get(allergen.lower(), ["No substitute found"])
    return {"substitution_suggestions": results}

@app.post("/generate_meal_plan_by_user_data")
def generate_meal_plan_by_user_data(data: dict):
    """
    Accepts user data (age, weight, height, activity_level, allergies, cuisine),
    calculates daily calorie target, and finds a set of recipes
    that sum approximately to that target.
    """
    # ---- 1️⃣ Extract User Inputs ----
    age = data["age"]
    weight = data["weight"]
    height = data["height"]
    activity_level = data.get("activity_level", "sedentary")
    allergies = [a.lower() for a in data.get("allergies", [])]
    selected_cuisine = data.get("cuisine", "").lower()

    # ---- 2️⃣ Calculate BMR and Daily Calorie Target ----
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
    activity_map = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
    multiplier = activity_map.get(activity_level.lower(), 1.2)
    daily_calorie_target = round(bmr * multiplier)

    # ---- 3️⃣ Find Recipes Closest to Target ----
    tolerance = 100
    selected_recipes = []
    used_recipes = set()
    total_calories = 0.0

    sorted_recipes = sorted(
        recipes.items(),
        key=lambda x: estimate_calories(x[1].get("ingredients", [])), 
        reverse=True
    )

    for name, recipe_data in sorted_recipes:
        # If a specific cuisine is requested, skip recipes NOT matching that
        if selected_cuisine and recipe_data.get("cuisine", "").lower() != selected_cuisine:
            continue

        modified_ingredients = []
        contains_allergen = False

        for ing in recipe_data.get("ingredients", []):
            lower_ing = ing.lower()
            substituted_ing = None
            for allergen in allergies:
                if allergen in lower_ing:
                    substituted_ing = substitutions.get(allergen, ["no substitute found"])[0]
                    contains_allergen = True
                    break
            modified_ingredients.append({
                "original": ing,
                "substitution": substituted_ing if substituted_ing else ing,
                "allergen_detected": bool(substituted_ing),
            })

        estimated_cal = estimate_calories(recipe_data.get("ingredients", []))

        if total_calories + estimated_cal <= daily_calorie_target + tolerance:
            selected_recipes.append({
                "name": name,
                "calories": estimated_cal,
                "ingredients": modified_ingredients,
                "steps": recipe_data.get("steps", []),
                "prep_time": recipe_data.get("prep_time", ""),
                "cook_time": recipe_data.get("cook_time", ""),
                "total_time": recipe_data.get("total_time", ""),
                "cuisine": recipe_data.get("cuisine", ""),
                "course": recipe_data.get("course", ""),
                "diet": recipe_data.get("diet", "")
            })
            used_recipes.add(name)
            total_calories += estimated_cal

        if daily_calorie_target - tolerance <= total_calories <= daily_calorie_target + tolerance:
            break
       # ---- 5️⃣ Divide selected recipes by course ----
    courses = {"breakfast": [], "lunch": [], "dinner": [], "other": []}
    for item in selected_recipes:
        course_name = item.get("course", "").lower()
        if "breakfast" in course_name:
            courses["breakfast"].append(item)
        elif "main" in course_name or "lunch" in course_name:
            courses["lunch"].append(item)
        elif "dinner" in course_name or "side" in course_name:
            courses["dinner"].append(item)
        else:
            courses["other"].append(item)

    # ---- Final Output ----
    return {
        "age": age,
        "weight": weight,
        "height": height,
        "bmi": round(bmi, 2),
        "daily_calorie_target": daily_calorie_target,
        "count": len(selected_recipes),
        "total_calories": round(total_calories, 2),
        "difference": round(daily_calorie_target - total_calories, 2),
        "cuisine": selected_cuisine if selected_cuisine else "all",
        "meals_by_course": courses
    }

@app.get("/available_courses")
def available_courses():
    """Return a sorted list of unique courses in the dataset."""
    courses = {
        recipe_data.get("course", "").strip()
        for recipe_data in recipes.values()
        if recipe_data.get("course", "").strip()
    }
    return {"available_courses": sorted(courses)}






@app.get("/ping")
def ping():
    return {"status": "ok"}
