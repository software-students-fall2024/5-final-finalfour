from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
import bcrypt


# --------SETUP FLASK & MONGODB--------
from dotenv import load_dotenv
load_dotenv() # load .env file
app = Flask(__name__)
app.secret_key = ("this_is_my_random_secret_key_987654321")
MONGO_URI = ("mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?tlsAllowInvalidCertificates=true")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI) # create MongoDB client
    db = client[MONGO_DBNAME]       # access database
    users_collection = db["users"]  # collection of users
    bars_collection = db["bars"]    # collection of bars
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise


# --------ACCOUNT PAGE--------
@app.route("/account")
def account():
    return render_template("account.html") # link to account.html


# --------LOGIN PAGE--------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get data
        username = request.form.get("username")
        password = request.form.get("password")

        # authenticate user
        user = users_collection.find_one({"username": username})

        if user and user["password"] == password:
            session["user_id"] = str(user["_id"])   # set session user_id
            session["username"] = user["username"]  # set session username
            return redirect(url_for("index"))       # direct to index.html
        else: return redirect(url_for("login"))

    return render_template("login.html") # link to login.html


# --------SIGNUP PAGE--------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # get data
        username = request.form.get("username")
        password = request.form.get("password")

        # check if user exists
        existing_user = users_collection.find_one({"username":username})
        if existing_user: return redirect(url_for("signup"))
        
        # insert new user into users collection
        users_collection.insert_one({"username":username, "password":password})
        return redirect(url_for("login")) # direct to login.html

    return render_template("signup.html") # link to signup.html


# --------HOME PAGE--------
@app.route("/")
def index():
    if "user_id" not in session: 
        return redirect(url_for("account")) # direct to login.html
    
    # get all bars from current user
    user_id = session.get("user_id")
    bars = bars_collection.find({"user_id": user_id})
    
    return render_template("index.html", bars=bars, username=session.get("username"))


# --------ADD PAGE--------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # get data
        name = request.form.get("name")
        type = request.form.get("type")
        occasion = request.form.get("occasion")
        area = request.form.get("area")
        reservation = request.form.get("reservation")
        cost = request.form.get("cost")
        status = request.form.get("status")

        # insert new bars into bars_collection
        new_bar = {
            "user_id": session.get("user_id"),
            "name": name,
            "type": type,
            "occasion": occasion,
            "area": area,
            "reservation": reservation,
            "cost": cost,
            "status": status
        }
        bars_collection.insert_one(new_bar)
        return redirect(url_for("index")) # direct to index.html
    
    return render_template("add.html") # link to add.html


# --------EDIT PAGE-------- 
@app.route("/edit/<bar_id>", methods=["GET", "POST"])
def edit(bar_id):
    if "user_id" not in session: return redirect(url_for("login")) # direct to login.html

    # ensure it's current user's bars
    bar = bars_collection.find_one(
        {"_id": ObjectId(bar_id),
        "user_id": session.get("user_id")}
    )
    if not bar: 
        return redirect(url_for("index")) # direct to index.html

    if request.method == "POST":
        # get data
        name = request.form.get("name")
        type = request.form.get("type")
        occasion = request.form.get("occasion")
        area = request.form.get("area")
        reservation = request.form.get("reservation")
        cost = request.form.get("cost")
        status = request.form.get("status")

        # update bar
        bars_collection.update_one(
            {"_id": ObjectId(bar_id), "user_id": session.get("user_id")},
            {"$set": {
                "name": name,
                "type": type,
                "occasion": occasion,
                "area": area,
                "reservation": reservation,
                "cost": cost,
                "status": status
            }}
        )
        return redirect(url_for("index")) # direct to home page

    return render_template("edit.html", bar=bar) # link to html


# --------DELETE PAGE--------
@app.route("/delete/<bar_id>", methods=["GET", "POST"])
def delete(bar_id):
    if "user_id" not in session: 
        return redirect(url_for("login")) # direct to login.html

    # ensure it's current user's bar
    bar = bars_collection.find_one({
        "_id": ObjectId(bar_id),
        "user_id": session.get("user_id")}
    )
    if not bar: 
        return redirect(url_for("index")) # direct to index.html

    # delete bar
    if request.method == "POST":
        bars_collection.delete_one({"_id": ObjectId(bar_id), "user_id": session.get("user_id")})
        return redirect(url_for("index")) # direct to index.html

    return render_template("delete.html", bar=bar) # link to delete.html


# --------SEARCH PAGE--------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session: 
        return redirect(url_for("login")) # direct to login.html

    # query variables
    query = {"user_id": session.get("user_id")} # user-specific
    category = request.form.get("category")
    search_value = request.form.get(category)

    # query based on chosen category (partial vs exact matching)
    if category:
        if category == "name":
            if isinstance(search_value, str): query[category] = {"$regex": search_value, "$options": "i"} 
        else: 
            query[category] = search_value # exact matching (drown-drop cats)

    bars = list(bars_collection.find(query)) # search by category

    return render_template('search.html', bars=bars, category=category) # link to html


# --------SORT PAGE--------
@app.route("/sort", methods=["GET", "POST"])
def sort():
    if "user_id" not in session: 
        return redirect(url_for("login")) # direct to login.html

    if request.method == "POST":
        # get data
        category = request.form.get("category")
        order = request.form.get("order")
        
        # set sort order: 1 = ascending, -1 = descending
        if order == "asc": sort_order = 1
        else: sort_order = -1

        # query sort bars
        query = {"user_id": session.get("user_id")}
        bars = list(bars_collection.find(query).sort(category, sort_order))

        # noramlize status field
        for bar in bars:
            if bar.get("status") == "Not Visited": bar["status"] = "No"
            elif bar.get("status") == "Visited": bar["status"] = "Yes"

        return render_template("sort.html", bars=bars)

    return render_template("sort.html", bars=[]) # link to sort.html


# --------RECOMMENDATIONS PAGE--------
import sys
sys.path.append('../bar-recs')  # parent directory
from recommender import load_bars, preprocess_bars, compute_sim_matrix, recommend_bars

@app.route('/recs', methods=['GET'])
def recommend():
    user_id = session.get('user_id')  # get current user_ID

    # get user's visited bars from MongoDB
    user_bars = list(bars_collection.find({"user_id": ObjectId(user_id), "visited": "Yes"}))
    user_bar_names = [bar['name'] for bar in user_bars]

    # load bar data and preprocess
    bars_df = load_bars('../bar-recs/bars.json') # get bars
    bars_df = preprocess_bars(bars_df)           # preprocess
    cosine_sim = compute_sim_matrix(bars_df)     # sim matrix

    recommendations = recommend_bars(user_bar_names, bars_df, cosine_sim) # top 5 recs

    return render_template('recommend.html', bars=recommendations)


# --------LOGOUT PAGE--------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("account")) # link to account.html


# MAIN METHOD
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )