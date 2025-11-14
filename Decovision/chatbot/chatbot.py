from flask import Flask, request, jsonify, render_template
import pandas as pd
import re

app = Flask(__name__)

# Load CSV
df = pd.read_csv("IKEA.csv")

# Clean and generate proper product URLs
def generate_ikea_link(product_id):
    return f"https://www.ikea.com/sa/en/p/-{product_id}/"

df['link'] = df['item_id'].astype(str).apply(generate_ikea_link)

# Color and furniture keywords
colors = ['black', 'white', 'brown', 'other', 'grey', 'red', 'yellow',
          'pink', 'green', 'blue', 'purple', 'orange']
furnitures = ['table', 'stool', 'bed', 'other', 'sofa', 'desk', 'shelf',
              'cabinet', 'bookcase', 'bench', 'sideboard', 'chair', 'stand',
              'wardrobe', 'island']

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/chat', methods=['POST'])
def chat():
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
    app.run(debug=True)
