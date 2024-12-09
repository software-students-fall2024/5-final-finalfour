import pytest
from web_app.app import app, db, users_collection, bars_collection
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


# Test configuration
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"

    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def logged_in_user(client):
    # Create a test user
    username = "testuser"
    password = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Insert test user into database
    user = {"username": username, "password": hashed_password}
    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)


# Test configuration
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


# Clean the database before and after each test
@pytest.fixture(autouse=True)
def clean_database():
    users_collection.delete_many({})
    bars_collection.delete_many({})
    yield
    users_collection.delete_many({})
    bars_collection.delete_many({})


def test_index(client):
    response = client.get("/")
    assert response.status_code == 302
    assert b"Redirecting..." in response.data


def test_signup(client):
    response = client.post(
        "/signup", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 302  # Redirect to login
    assert users_collection.find_one({"username": "testuser"}) is not None


def test_login(client):
    hashed_password = bcrypt.hashpw("testpass".encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({"username": "testuser", "password": hashed_password})

    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_delete_transaction(client):
    username = "testuser"
    bar_id = bars_collection.insert_one(
        {"user_id": "test_user_id", "name": "Delete Me"}
    ).inserted_id

    with client.session_transaction() as sess:
        sess["user_id"] = "test_user_id"

    response = client.post(f"/delete/{bar_id}")
    assert response.status_code == 302
    assert bars_collection.find_one({"_id": bar_id}) is None


def test_edit_bar(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)
    bar_id = bars_collection.insert_one(
        {
            "user_id": user_id,
            "name": "Old Bar",
            "type": "Pub",
            "occasion": "Casual",
            "area": "Downtown",
            "reservation": "No",
            "cost": "$$",
            "status": "Visited",
        }
    ).inserted_id

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        f"/edit/{bar_id}",
        data={
            "type": "Bar",
            "occasion": "Date",
            "area": "Midtown",
            "reservation": "Yes",
            "cost": "$$$",
            "status": "Not Visited",
        },
    )
    assert response.status_code == 302
    updated_bar = bars_collection.find_one({"_id": bar_id})
    assert updated_bar["name"] == "Old Bar"  # Name should not change


def test_add_bar(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        "/add",
        data={
            "name": "New Bar",
            "type": "Pub",
            "occasion": "Casual",
            "area": "Downtown",
            "reservation": "Yes",
            "cost": "$$",
            "status": "Not Visited",
        },
    )
    assert response.status_code == 302
    assert bars_collection.find_one({"user_id": user_id, "name": "New Bar"}) is not None


def test_recommend_bars(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Mock bar data for recommendations
    bars_collection.insert_many(
        [{"user_id": user_id, "name": "Bar A"}, {"user_id": user_id, "name": "Bar B"}]
    )

    response = client.get("/recs")
    assert response.status_code == 200
    assert b"Bar A" not in response.data  # Recommendations exclude user's own bars


def test_search(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)
    bars_collection.insert_one(
        {"user_id": user_id, "name": "Search Bar", "type": "Pub"}
    )

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Search for the bar
    response = client.post("/search", data={"category": "name", "name": "Search Bar"})
    assert response.status_code == 200
    assert b"Search Bar" in response.data


def test_sort(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)
    bars_collection.insert_many(
        [
            {"user_id": user_id, "name": "Bar A", "cost": "$"},
            {"user_id": user_id, "name": "Bar B", "cost": "$$"},
        ]
    )

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Sort by cost in ascending order
    response = client.post("/sort", data={"category": "cost", "order": "asc"})
    assert response.status_code == 200
    assert b"Bar A" in response.data
    assert b"Bar B" in response.data


def test_edit_unauthorized(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)
    other_user_id = str(
        users_collection.insert_one({"username": "otheruser"}).inserted_id
    )

    # Bar belongs to another user
    bar_id = bars_collection.insert_one(
        {"user_id": other_user_id, "name": "Other Bar"}
    ).inserted_id

    # Log in as the unauthorized user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Try to edit the other user's bar
    response = client.get(f"/edit/{bar_id}")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Try submitting an edit to the other user's bar
    response = client.post(f"/edit/{bar_id}", data={"name": "Unauthorized Edit"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_delete_nonexistent_bar(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Try to delete a non-existent bar
    response = client.post("/delete/642ef1c9e55f1d439f6d8c3f")  # Random ObjectId
    assert response.status_code == 302  # Redirect to home
    assert response.headers["Location"] == "/"


def test_search_invalid_category(client):
    user_id = str(users_collection.insert_one({"username": "testuser"}).inserted_id)

    # Log in the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Search with an invalid category
    response = client.post(
        "/search", data={"category": "invalid_category", "search_query": "Bar"}
    )
    assert response.status_code == 200  # The response should still return 200

    # Verify that the response contains no results or is empty
    # Assuming no results would result in an empty table or no content in the results section
    assert (
        b"No results found" not in response.data
    )  # Confirm there's no misleading message
    assert (
        b"<!-- SEARCH DATA PAGE -->" in response.data
    )  # Ensure the HTML structure is still present
    assert b"Bar" not in response.data  # Ensure that "Bar" is not accidentally included
