import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from app.mock_data import recipes_df

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(recipes_df["ingredients"])
y = recipes_df["calories"]

model = LinearRegression()
model.fit(X, y)

def estimate_calories(ingredient_list):
    text = " ".join(ingredient_list)
    vec = vectorizer.transform([text])
    predicted = model.predict(vec)
    return round(predicted[0], 2)
    
