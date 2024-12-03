import os
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
import bcrypt

# Load environment variables
from dotenv import load_dotenv

# Load the .env file to access environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
# Get the secret key for session management from the environment variable
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB configuration
# MongoDB connection URI and database name from environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)  # Create a MongoDB client
    db = client[MONGO_DBNAME]  # Access the specified database
    users_collection = db["users"]  # Access the "users" collection
    bar_data_collection = db["bar"]  # Access the "bar" collection
except Exception as e:
    # Handle errors during the connection process
    print(f"Error connecting to MongoDB: {e}")
    raise


# Routes
@app.route("/")
def index():
    """Render the welcome page."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        # Get the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        # Find the user in the database
        user = users_collection.find_one({"username": username})
        # Check if the user exists and the password matches
        if user and bcrypt.checkpw(password, user["password"]):
            # Set session variables for the logged-in user
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session.permanent = False  # Session expires when the browser is closed
            flash("Login successful!", "success")  # Flash a success message
            return redirect(url_for("dashboard"))  # Redirect to the dashboard
        else:
            flash("Invalid username or password.", "error")  # Flash an error message

    return render_template("login.html")  # Render the login page


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    if request.method == "POST":
        # Get the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))  # Redirect back to the signup page

        # Hash the password for secure storage
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # Insert the new user into the database
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash(
            "Account created successfully. Please log in.", "success"
        )  # Flash success message
        return redirect(url_for("login"))  # Redirect to the login page

    return render_template("signup.html")  # Render the signup page


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.clear()  # Clear the user's session
    flash("You have been logged out.", "success")  # Flash a success message
    return redirect(url_for("index"))  # Redirect to the welcome page


@app.route("/dashboard")
def dashboard():
    """Render user dashboard."""
    # Ensure the user is logged in
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))  # Redirect to the login page if not logged in

    # Get the username from the session
    username = session.get("username", "User")
    # Render the dashboard page with the username
    return render_template("dashboard.html", username=username)


# Application entry point
if __name__ == "__main__":
    # Run the Flask app with host, port, and debug mode configurations from environment variables
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )
