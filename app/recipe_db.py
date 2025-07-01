import json
from pathlib import Path

def load_recipes():
    path = Path(__file__).parent / "recipes.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

recipes = load_recipes()
