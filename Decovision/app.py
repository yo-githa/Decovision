from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the user database
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

# Generate product links
def generate_ikea_link(product_id):
    return f"https://www.ikea.com/sa/en/p/-{product_id}/"

df['link'] = df['item_id'].astype(str).apply(generate_ikea_link)

# Color and furniture keywords
colors = ['black', 'white', 'brown', 'other', 'grey', 'red', 'yellow',
          'pink', 'green', 'blue', 'purple', 'orange']
furnitures = ['table', 'stool', 'bed', 'other', 'sofa', 'desk', 'shelf',
              'cabinet', 'bookcase', 'bench', 'sideboard', 'chair', 'stand',
              'wardrobe', 'island']

# Routes
@app.route('/')
def index():
    return render_template('index1.html')

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

@app.route('/quiz')
def quiz():
    return "Quiz page coming soon!"

@app.route('/redefine')
def redefine():
    return "Redefine Your Space - coming soon!"

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat1.html')

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
