import logging
import pytest
from app import app, db
from models.db_models import User, Movie

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler("app.log"),  # Log to file 'app.log'
        logging.StreamHandler(),  # Continue logging to the terminal
    ],
)
logging.basicConfig(
    level=logging.ERROR,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler("app.log"),  # Log to file 'app.log'
        logging.StreamHandler(),  # Continue logging to the terminal
    ],
)



@pytest.fixture
def client():
    """Fixture to set up a Flask test client."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the database and tables for testing
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests


def test_home_page(client):
    """Test if the home page loads correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"MovieWeb App" in response.data  # Check if the title appears in the HTML


def test_list_users_empty(client):
    """Test if the users list page shows no users when empty."""
    response = client.get("/users")
    assert response.status_code == 200
    assert b"No users found" in response.data  # Assuming there's a message for empty users


def test_add_user(client):
    """Test adding a new user."""
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test User" in response.data  # Check if the user is added to the list


def test_add_movie(client):
    """Test adding a movie for an existing user."""
    # First, add a user
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert b"Test User" in response.data

    logging.info("User added successfully.")
    logging.info(response.data)
    
    # Now add a movie for that user
    response = client.post(
        "/users/1/add_movie",
        data={
            "name": "Test Movie",
            "director": "Test Director",
            "year": "2024",
            "rating": "8.5"
        },
        follow_redirects=True
    )
    print(response.data)  # Log the response data for debugging
    assert response.status_code == 200
    assert b"Test Movie" in response.data  # Check if the movie was added



def test_404_error(client):
    """Test if a 404 page is shown for an invalid URL."""
    response = client.get("/nonexistent_page")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data  # Assuming your 404.html has this text


def test_delete_movie(client):
    """Test deleting a movie."""
    # Add user and movie first
    client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    client.post(
        "/users/1/add_movie",
        data={
            "name": "Test Movie",
            "director": "Test Director",
            "year": "2024",
            "rating": "8.5"
        },
        follow_redirects=True
    )

    # Now delete the movie
    response = client.post("/users/1/delete_movie/1", follow_redirects=True)
    print(response.data)  # Log the response for debugging
    assert response.status_code == 200
    assert b"Test Movie" not in response.data  # Ensure the movie is deleted
