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
import pandas as pd
import json

# --------SETUP FLASK & MONGODB--------
from dotenv import load_dotenv

load_dotenv()  # load .env file
app = Flask(__name__)
app.secret_key = "this_is_my_random_secret_key_987654321"
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?tlsAllowInvalidCertificates=true",
)
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "finalfour")

# Connect to MongoDB
client = MongoClient(MONGO_URI)  # create MongoDB client
db = client[MONGO_DBNAME]  # access database
users_collection = db["users"]  # collection of users
bars_collection = db["bars"]  # collection of bars


# --------ACCOUNT PAGE--------
@app.route("/account")
def account():
    return render_template("account.html")  # link to account.html


# --------LOGIN PAGE--------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        raw_password = request.form["password"].strip()

        # Encode the entered password to bytes
        password_bytes = raw_password.encode("utf-8")

        # Find the user in the database
        user = users_collection.find_one({"username": username})

        if user and "password" in user:
            # user["password"] should be the hashed bytes stored at signup
            stored_hashed_password = user["password"]

            # Check the password using bcrypt
            if bcrypt.checkpw(password_bytes, stored_hashed_password):
                # Password matches, log the user in
                session["user_id"] = str(user["_id"])
                session["username"] = username
                session.permanent = False
                return redirect(url_for("index"))
            else:
                # Incorrect password
                flash("Invalid username or password.", "error")
                return redirect(url_for("login"))
        else:
            # User not found
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    # GET request just renders the login template
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        raw_password = request.form["password"].strip()

        # Encode the password to bytes
        password_bytes = raw_password.encode("utf-8")
        # Check if username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))

        # Hash the password (bcrypt.hashpw returns bytes)
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# --------HOME PAGE--------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("account"))  # direct to login.html

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
            "status": status,
        }
        bars_collection.insert_one(new_bar)
        return redirect(url_for("index"))  # direct to index.html

    return render_template("add.html")  # link to add.html


# --------EDIT PAGE--------
@app.route("/edit/<bar_id>", methods=["GET", "POST"])
def edit(bar_id):
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html

    # ensure it's current user's bars
    bar = bars_collection.find_one(
        {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
    )
    if not bar:
        return redirect(url_for("index"))  # direct to index.html

    if request.method == "POST":
        # get data
        name = bar["name"] # get bar name
        type = request.form.get("type")
        occasion = request.form.get("occasion")
        area = request.form.get("area")
        reservation = request.form.get("reservation")
        cost = request.form.get("cost")
        status = request.form.get("status")

        # update bar
        bars_collection.update_one(
            {"_id": ObjectId(bar_id), "user_id": session.get("user_id")},
            {
                "$set": {
                    "name": name,
                    "type": type,
                    "occasion": occasion,
                    "area": area,
                    "reservation": reservation,
                    "cost": cost,
                    "status": status,
                }
            },
        )
        return redirect(url_for("index"))  # direct to home page

    return render_template("edit.html", bar=bar)  # link to html


# --------DELETE PAGE--------
@app.route("/delete/<bar_id>", methods=["GET", "POST"])
def delete(bar_id):
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html

    # ensure it's current user's bar
    bar = bars_collection.find_one(
        {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
    )
    if not bar:
        return redirect(url_for("index"))  # direct to index.html

    # delete bar
    if request.method == "POST":
        bars_collection.delete_one(
            {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
        )
        return redirect(url_for("index"))  # direct to index.html

    return render_template("delete.html", bar=bar)  # link to delete.html


# --------SEARCH PAGE--------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html
    
    bars = []
    category = None

    if request.method == "POST":
        # query variables
        query = {"user_id": session.get("user_id")}  # user-specific
        category = request.form.get("category")
        search_value = request.form.get(category)

        # query based on chosen category (partial vs exact matching)
        if category:
            if category == "Name":
                if isinstance(search_value, str):
                    query[category] = {"$regex": search_value, "$options": "i"}
            else:
                query[category] = search_value  # exact matching (drown-drop cats)

        bars = list(bars_collection.find(query))  # search by category

    else: flash("Please select a category and enter a value.", "warning")

    return render_template("search.html", bars=bars, category=category)  # link to html


# --------SORT PAGE--------
@app.route("/sort", methods=["GET", "POST"])
def sort():
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html

    if request.method == "POST":
        # get data
        category = request.form.get("category")
        order = request.form.get("order")

        # set sort order: 1 = ascending, -1 = descending
        if order == "asc":
            sort_order = 1
        else:
            sort_order = -1

        # query sort bars
        query = {"user_id": session.get("user_id")}
        bars = list(bars_collection.find(query).sort(category, sort_order))

        # noramlize status field
        for bar in bars:
            if bar.get("status") == "Not Visited":
                bar["status"] = "No"
            elif bar.get("status") == "Visited":
                bar["status"] = "Yes"

        return render_template("sort.html", bars=bars)

    return render_template("sort.html", bars=[])  # link to sort.html


# --------RECOMMENDATIONS PAGE--------
from web_app.recommender.recommender import (
    load_bars,
    preprocess_bars,
    compute_sim_matrix,
    recommend_bars,
)
@app.route("/recs", methods=["GET", "POST"])
def recommend():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Get user's bars from MongoDB
    user_bars = list(bars_collection.find({"user_id": user_id}))
    user_bar_names = [bar["name"] for bar in user_bars]

    # Load and preprocess bar data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bars_json_path = os.path.join(current_dir, "recommender", "bars.json")

    if not os.path.exists(bars_json_path):
        raise FileNotFoundError(f"bars.json file not found at {bars_json_path}")

    with open(bars_json_path, "r") as file:
        bars_data = json.load(file)

    bars_df = pd.json_normalize(bars_data) # normalize JSON into DF

    required_columns = [
        "Name",
        "Type",
        "Occasion",
        "Area",
        "Reservation",
        "Cost"
    ]
    if not all(col in bars_df.columns for col in required_columns):
        raise ValueError(
            f"The JSON data is missing required columns: {required_columns}"
        )
    bars_df = bars_df[required_columns] # select required
    bars_df = bars_df[~bars_df["Name"].isin(user_bar_names)] # remove existing bars from recs

    # preprocess/compute recommendations
    bars_df = preprocess_bars(bars_df)
    cosine_sim = compute_sim_matrix(bars_df)
    recommendations = recommend_bars(user_bar_names, bars_df, cosine_sim)
    while len(recommendations) < 5 and len(bars_df) > len(recommendations):
        for _, bar in bars_df.iterrows():
            if bar["Name"] not in [rec["name"] for rec in recommendations]:
                recommendations.append(
                    {
                        "name": bar["Name"],
                        "type": bar["Type"],
                        "occasion": bar["Occasion"],
                        "area": bar["Area"],
                        "reservation": bar["Reservation"],
                        "cost": bar["Cost"],
                    }
                )
                if len(recommendations) == 5:
                    break

    if request.method == "POST":
        bar_name = request.form.get("bar_name")
        if bar_name:
            bar_to_add = next(
                (bar for bar in recommendations if bar["name"] == bar_name), None
            )
            # add bar to user's database
            if bar_to_add:
                new_bar = {
                    "user_id": user_id,
                    "name": bar_to_add["name"],
                    "type": bar_to_add["type"],
                    "occasion": bar_to_add["occasion"],
                    "area": bar_to_add["area"],
                    "reservation": bar_to_add["reservation"],
                    "cost": bar_to_add["cost"],
                    "status": "Not Visited",
                }
                bars_collection.insert_one(new_bar)
                flash(f"Added {bar_name} to your list!", "success")
                return redirect(url_for("recommend"))

    return render_template("recommend.html", bars=recommendations)


# --------LOGOUT PAGE--------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("account"))  # link to account.html


# MAIN METHOD
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )
