from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv(
    "MONGO_URI",
    "mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?retryWrites=true&w=majority",
)
app.config["SECRET_KEY"] = "this_is_my_random_secret_key_987654321"
# Initialize MongoDB
mongo = PyMongo(app)
db = mongo.db


def load_ratings_data():
    """
    Fetch ratings from MongoDB and prepare Surprise dataset.
    """
    ratings = list(db.ratings.find())  # Example MongoDB collection: 'ratings'
    if not ratings:
        # Return None if no ratings are present
        return None

    # Convert MongoDB ratings to pandas DataFrame
    df = pd.DataFrame(ratings)

    # Define a Surprise Reader object
    reader = Reader(rating_scale=(1, 5))  # Assuming a rating scale of 1 to 5
    return Dataset.load_from_df(df[["user_id", "bar_id", "rating"]], reader)


# def load_ratings_data():
#     """
#     Fetch ratings from MongoDB and prepare Surprise dataset.
#     """
#     ratings = list(db.ratings.find())  # Example MongoDB collection: 'ratings'
#     if not ratings:
#         # Return an empty Surprise Dataset if no ratings are present
#         return None

#     # Convert MongoDB ratings to Surprise-compatible format
#     data = []
#     for rating in ratings:
#         data.append((rating['user_id'], rating['bar_id'], rating['rating']))

#     # Define a Surprise Reader object
#     reader = Reader(rating_scale=(1, 5))  # Assuming a rating scale of 1 to 5
#     return Dataset.load_from_df(data, reader)


# Initialize the recommender system
def train_recommender_system():
    """
    Train the Surprise recommender system using SVD.
    """
    data = load_ratings_data()
    if data is None:
        return None, None

    trainset, testset = train_test_split(data, test_size=0.2)
    algo = SVD()  # Using SVD for collaborative filtering
    algo.fit(trainset)

    # Evaluate the model (optional, for debugging purposes)
    predictions = algo.test(testset)
    accuracy.rmse(predictions)

    return algo, trainset


recommender_algo, recommender_trainset = train_recommender_system()


# Models
def add_bar(bar_data):
    """Add a new bar to the database."""
    return db.bars.insert_one(bar_data)


def get_all_bars():
    """Fetch all bars from the database."""
    return list(db.bars.find())


def add_rating(rating_data):
    """
    Add a new rating to the database.
    Example: {"user_id": "1", "bar_id": "101", "rating": 4.5}
    """
    return db.ratings.insert_one(rating_data)


def recommend_bars_for_user(user_id):
    """
    Recommend bars for a specific user using collaborative filtering.

    Parameters:
        user_id: ID of the user requesting recommendations.

    Returns:
        List of recommended bar IDs.
    """
    if recommender_algo is None:
        return []

    # Generate predictions for bars the user hasn't rated yet
    all_bars = get_all_bars()
    user_ratings = db.ratings.find({"user_id": user_id})
    rated_bar_ids = {rating["bar_id"] for rating in user_ratings}

    recommendations = []
    for bar in all_bars:
        if str(bar["_id"]) not in rated_bar_ids:  # Only recommend unrated bars
            pred = recommender_algo.predict(user_id, str(bar["_id"]))
            recommendations.append((bar, pred.est))  # Append bar and estimated rating

    # Sort recommendations by predicted rating, descending
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in recommendations[:5]]  # Return top 5 recommendations


# Routes
@app.route("/add_bar", methods=["POST"])
def add_bar_route():
    """Add a new bar to the database."""
    data = request.get_json()
    result = add_bar(data)
    return jsonify({"success": True, "bar_id": str(result.inserted_id)}), 201


@app.route("/add_rating", methods=["POST"])
def add_rating_route():
    """Add a user rating for a bar."""
    data = request.get_json()
    result = add_rating(data)
    return jsonify({"success": True, "rating_id": str(result.inserted_id)}), 201


@app.route("/get_bars", methods=["GET"])
def get_bars():
    """Get all bars."""
    bars = get_all_bars()
    return jsonify(bars), 200


@app.route("/recommend/<user_id>", methods=["GET"])
def recommend(user_id):
    """
    Get bar recommendations for a user.

    Parameters:
        user_id: ID of the user requesting recommendations.
    """
    recommendations = recommend_bars_for_user(user_id)
    return jsonify(recommendations), 200


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
