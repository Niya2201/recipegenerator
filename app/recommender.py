from app.mock_data import recipes

def recommend_meals(preferences, allergies, max_calories=None):
    suggested = []
    for meal in recipes:
        if not set(preferences).intersection(meal["diet"]):
            continue
        if any(allergy.lower() in meal["ingredients"].lower() for allergy in allergies):
            continue
        if max_calories and meal["calories"] > max_calories:
            continue
        suggested.append(meal)
    return suggested
