import spacy

nlp = spacy.load("en_core_web_sm")

allergen_map = {
    "milk": "almond milk",
    "peanut butter": "sunflower seed butter",
    "honey": "maple syrup"
}

def replace_allergens(ingredients, allergies):
    updated = []
    for ing in ingredients:
        ing_lower = ing.lower()
        if ing_lower in allergies:
            updated.append(allergen_map.get(ing_lower, "safe alternative"))
        else:
            updated.append(ing)
    return updated
