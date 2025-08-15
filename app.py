from flask import Flask, request, render_template
import pandas as pd
import random
import pickle
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ================================================================
# 1️⃣ Load Pre-trained Models & Data
# ================================================================
with open("models/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("models/cosine_sim.pkl", "rb") as f:
    cosine_sim = pickle.load(f)

products = pd.read_csv("models/products.csv")

# ================================================================
# 2️⃣ Database Configuration
# ================================================================
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ecom"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ================================================================
# 3️⃣ Utility Functions
# ================================================================
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "..."
    return text

def random_price():
    return random.choice([40,50,60,70,100,122,106,50,30,50])

def content_based_recommendations(item_name, top_n=10):
    if item_name not in products['Name'].values:
        return pd.DataFrame()
    idx = products[products['Name'] == item_name].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:top_n+1]
    product_indices = [i[0] for i in sim_scores]
    return products.iloc[product_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

# ================================================================
# 4️⃣ Routes
# ================================================================
random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]

@app.route("/")
def index():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(products))]
    return render_template(
        'index.html',
        trending_products=products.head(8),
        truncate=truncate,
        random_product_image_urls=random_product_image_urls,
        random_price=random_price
    )

@app.route("/main", methods=['GET','POST'])
def main():
    search_query = ""
    recommended_products = pd.DataFrame()
    if request.method == 'POST':
        search_query = request.form.get('search')
        recommended_products = content_based_recommendations(search_query, top_n=8)
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(recommended_products))]
    return render_template('main.html',
                           search_query=search_query,
                           recommended_products=recommended_products,
                           truncate=truncate,
                           random_product_image_urls=random_product_image_urls,
                           random_price=random_price
                           )

@app.route("/signup", methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    new_signup = Signup(username=username, email=email, password=password)
    db.session.add(new_signup)
    db.session.commit()
    return index()

@app.route("/signin", methods=['POST'])
def signin():
    username = request.form['signinUsername']
    password = request.form['signinPassword']
    new_signin = Signin(username=username, password=password)
    db.session.add(new_signin)
    db.session.commit()
    return index()

if __name__ == "__main__":
    app.run(debug=True)
