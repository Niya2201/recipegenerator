from pydantic import BaseModel
from typing import List, Optional

class MealRequest(BaseModel):
    preferences: List[str]
    allergies: List[str]
    calories_per_meal: Optional[int] = None

class AllergenInput(BaseModel):
    ingredients: List[str]
    allergies: List[str]

class NutritionInput(BaseModel):
    ingredients: List[str]

class CalorieEstimateInput(BaseModel):
    ingredients: List[str]
class DishRequest(BaseModel):
    dish_name: str
    exact_match: bool = False
class UserProfileInput(BaseModel):
    age: int
    weight: float  # in kg
    height: float  # in cm
    activity_level: str  # "sedentary", "light", "moderate", "active"
    allergies: List[str]  
class SubstitutionRequest(BaseModel):
    allergies: List[str]   
from pydantic import BaseModel
from typing import List

class RecipeByCalorieRequest(BaseModel):
    target_calories: float
    tolerance: float
    allergies: List[str]


