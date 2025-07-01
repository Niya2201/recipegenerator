import React, { useState, useRef } from "react";
import "./App.css";

export default function App() {
  const [dish, setDish] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);
  const [recipeResult, setRecipeResult] = useState(null);
  const [error, setError] = useState(null);
  const [showLanding, setShowLanding] = useState(true); // Landing page visibility
  const resultRef = useRef(null);

  async function fetchRecipe() {
    setError(null);
    setRecipeResult(null);

    try {
      if (selectedImage) {
        const formData = new FormData();
        formData.append("image_file", selectedImage);

        const res = await fetch("http://127.0.0.1:8000/predict_and_recipe/", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const errorData = await res.json();
          setError(errorData.detail || "Error retrieving recipe from image");
          return;
        }

        const data = await res.json();
        setRecipeResult({ prediction: data.predicted_label, results: data.results });

      } else if (dish.trim()) {
        const res = await fetch("http://127.0.0.1:8000/recipe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dish_name: dish }),
        });

        if (!res.ok) {
          const errorData = await res.json();
          setError(errorData.detail || "Error retrieving recipe");
          return;
        }

        const data = await res.json();
        setRecipeResult({ prediction: dish, results: data.results });

      } else {
        alert("Please enter a dish name or select an image.");
        return;
      }

      // Scroll to results after loading
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);

    } catch (err) {
      setError("Unexpected error occurred.");
    }
  }

  return (
    <div className="app-background">
      <div className="overlay"></div>

      {/* Landing Page */}
      {showLanding && (
        <div className="landing-page">
          <h1 className="landing-title">Let's Eat Healthy 🥗</h1>
          <button className="enter-btn" onClick={() => setShowLanding(false)}>
            SERVE  IT  FOR  YOURSELF!!! 
          </button>

        </div>
      )}

      {/* Main Form and Result */}
      {!showLanding && (
        <>
          {/* Form Section */}
          <div className="form-wrapper">
            <div className="form-container slide-in">
              <h1> Recipe & Calorie  Generator</h1>

              <label>Dish Name:</label>
              <input
                type="text"
                value={dish}
                onChange={(e) => setDish(e.target.value)}
                placeholder="e.g. masala karela"
              />

              <label>Upload Dish Image:</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setSelectedImage(e.target.files[0])}
              />

              <button onClick={fetchRecipe}>Get Recipe</button>

              {error && <div className="error">{error}</div>}
            </div>
          </div>

          {/* Result Section */}
          {recipeResult && (
            <div className="result-section fade-in" ref={resultRef}>
              <div className="result-container">
                <h2 style={{ color: "white", textShadow: "1px 1px 4px black" }}>
                  PREDICTED DISH: {recipeResult.prediction}
                </h2>
                {Object.entries(recipeResult.results).map(([name, details]) => (
                  <div className="card" key={name}>
                    <h3>{name}</h3>
                    <p><strong>Cuisine:</strong> {details.cuisine}</p>
                    <p><strong>Course:</strong> {details.course}</p>
                    <p><strong>Diet:</strong> {details.diet}</p>
                    <p><strong>Estimated Calories:</strong> {details.estimated_calories} kcal</p>

                    <h4>Ingredients:</h4>
                    <ul>
                      {details.ingredients.map((ing, i) => <li key={i}>{ing}</li>)}
                    </ul>

                    <h4>Steps:</h4>
                    <ol>
                      {details.steps.map((step, i) => <li key={i}>{step}</li>)}
                    </ol>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
