from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import re
import json
import random
import pickle
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize user database
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                        )''')

# Load IKEA data
df = pd.read_csv("IKEA.csv")

def generate_ikea_link(product_id):
    return f"https://www.ikea.com/sa/en/p/-{product_id}/"

df['link'] = df['item_id'].astype(str).apply(generate_ikea_link)

colors = ['black', 'white', 'brown', 'other', 'grey', 'red', 'yellow', 'pink', 'green', 'blue', 'purple', 'orange']
furnitures = ['table', 'stool', 'bed', 'other', 'sofa', 'desk', 'shelf', 'cabinet', 'bookcase', 'bench', 'sideboard', 'chair', 'stand', 'wardrobe', 'island']

# Load quiz data
with open("quiz_data.json", "r", encoding="utf-8") as file:
    quiz_data = json.load(file)



# -------------------- ROUTES ----------------------

@app.route('/')
def index():
    return render_template('index10.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, password FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session['user'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/redefine')
def redefine():
    return "Redefine Your Space - coming soon!"

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat2.html')

    query = request.json.get('message', '').lower()
    price_range = (0, float('inf'))

    if match := re.search(r'between\s*(\d+)\s*and\s*(\d+)', query):
        price_range = (int(match.group(1)), int(match.group(2)))
    elif match := re.search(r'(?:under|below|less than)\s*(\d+)', query):
        price_range = (0, int(match.group(1)))
    elif match := re.search(r'(?:over|above|more than)\s*(\d+)', query):
        price_range = (int(match.group(1)), float('inf'))
    elif match := re.search(r'\b(\d{2,5})\b', query):
        base_price = int(match.group(1))
        delta = int(0.2 * base_price)
        price_range = (base_price - delta, base_price + delta)

    color = next((c for c in colors if c in query), None)
    furniture = next((f for f in furnitures if f in query), None)

    filtered = df[df['price'].between(*price_range)]
    if color:
        filtered = filtered[filtered['basic_color'].str.contains(color, na=False, case=False)]
    if furniture:
        filtered = filtered[filtered['category'].str.contains(furniture, na=False, case=False)]

    result = filtered[['item_id', 'name', 'category', 'price', 'short_description', 'link', 'basic_color']].head(6)
    return jsonify(result.to_dict(orient='records'))

# ----------------- QUIZ ROUTES ----------------------

@app.route('/quiz', methods=['GET'])
def quiz():
    colors = sorted(set(item["Color"] for item in quiz_data))
    materials = sorted(set(item["Material"] for item in quiz_data))
    patterns = sorted(set(item["Pattern"] for item in quiz_data))
    lightings = sorted(set(item["Lighting"] for item in quiz_data))

    return render_template("quiz_ui.html", colors=colors, materials=materials, patterns=patterns, lightings=lightings)

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
            f"static/images/{style.lower()}.jpeg" if os.path.exists(f"static/images/{style.lower()}.jpeg") else "static/images/default.jpg"
            for style in unique_styles
        ]

        return render_template("result.html", styles=unique_styles, images=images, user_inputs=user_preferences)

    return render_template("result.html", styles=["No Match Found"], images=["static/images/default.jpg"], user_inputs=user_preferences)

# -------------------- MAIN ----------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
