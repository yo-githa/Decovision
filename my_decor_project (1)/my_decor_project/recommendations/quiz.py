from flask import Flask, render_template, request, jsonify
import json
import pickle
import random
import os

app = Flask(__name__)

# Load the quiz data from JSON
with open("quiz_data.json", "r", encoding="utf-8") as file:
    quiz_data = json.load(file)

# Load the model (if needed for future improvements)
with open("quiz.pkl", "rb") as f:
    model = pickle.load(f)

@app.route("/")
def index():
    """Load the quiz page with dynamically generated options."""
    colors = list(set(item["Color"] for item in quiz_data))
    materials = list(set(item["Material"] for item in quiz_data))
    patterns = list(set(item["Pattern"] for item in quiz_data))
    lightings = list(set(item["Lighting"] for item in quiz_data))

    return render_template("index.html", colors=colors, materials=materials, patterns=patterns, lightings=lightings)


@app.route("/recommend", methods=["POST"])
def recommend():
    user_preferences = request.form.to_dict()

    matching_items = [
        item for item in quiz_data if 
        item["Color"].strip().lower() == user_preferences["color"].strip().lower() and
        item["Material"].strip().lower() == user_preferences["material"].strip().lower() and
        item["Pattern"].strip().lower() == user_preferences["pattern"].strip().lower() and
        item["Lighting"].strip().lower() == user_preferences["lighting"].strip().lower()
    ]

    if matching_items:
        random.shuffle(matching_items)
        unique_styles = []
        for item in matching_items:
            if item["Style Suggestion"] not in unique_styles:
                unique_styles.append(item["Style Suggestion"])
            if len(unique_styles) == 2:
                break

        images = [
            "static/images/modern.jpeg" if style == "Modern" else
            "static/images/bohemian.jpeg" if style == "Bohemian" else
            "static/images/classic.jpeg" if style == "Classic" else
            "static/images/minimalist.jpeg" if style == "Minimalist" else
            "static/images/rustic.jpeg" if style == "Rustic" else
            "static/images/industrial.jpeg" if style == "Industrial" else
            "static/images/scandinavian.jpeg" if style == "Scandinavian" else
            "static/images/default.jpg"
            for style in unique_styles
        ]

        return render_template("result.html", styles=unique_styles, images=images, user_inputs=user_preferences)

    return render_template("result.html", styles=["No Match Found"], images=["static/images/default.jpg"], user_inputs=user_preferences)

if __name__ == "__main__":
    app.run(debug=True)
