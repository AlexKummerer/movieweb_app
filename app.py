from flask import (
    Flask,
    current_app,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
import requests
from forms.add_movie_form import AddMovieForm
from models.data_manager import SQLiteDataManager as DataManager
from models import db
from models.db_models import Movie, User
import logging
from forms.add_user_from import AddUserForm

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

app = Flask(__name__)
app.debug = True
app.config.from_object("config.Config")
csrf = CSRFProtect(app)

# Initialize the data manager and the database
db.init_app(app)
data_manager = DataManager(app)


def fetch_movie_details_from_omdb(title):
    """Fetch movie details from the OMDb API by movie title."""
    api_key = current_app.config.get("OMDB_API_KEY")  # Get the API key from the config
    url = f"http://www.omdbapi.com/?t={title}&plot=full&apikey={api_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data["Response"] == "True":
            # Extract the necessary details
            movie_details = {
                "name": data.get("Title"),
                "director": data.get("Director"),
                "year": data.get("Year"),
                "rating": data.get("imdbRating"),
            }
            return movie_details
        else:
            return None  # Movie not found
    else:
        raise Exception(
            f"OMDb API request failed with status code {response.status_code}"
        )


# ----------- Routes -----------


ERROR_TEMPLATE = "error.html"


@app.route("/", methods=["GET", "POST"])
def home():

    return render_template("home.html")


@app.route("/users")
def list_users():
    """Route to display the list of users."""
    try:
        users = data_manager.get_all_users()
        logging.info(f"Retrieved {len(users)} users.")
        return render_template("users.html", users=users)
    except Exception as e:
        logging.error(f"Error retrieving users: {e}")
        return render_template(ERROR_TEMPLATE, message="Error loading users."), 500


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Route to handle adding a new user."""
    logging.info("Handling add_user request.")
    form: AddUserForm = AddUserForm()  # Create an instance of your form

    if request.method == "POST" and form.validate_on_submit():
        try:

            name = form.name.data
            new_user = User(name=name)
            data_manager.add_user(new_user)
            logging.info(f"User '{name}' added successfully.")
            return redirect(url_for("list_users"))

        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return render_template(ERROR_TEMPLATE, message="Error adding user."), 500

    return render_template("add_user.html", form=form)


@app.route("/user/<int:user_id>")
def user_movies(user_id):
    """Route to display a user's movies."""
    logging.info(f"Fetching movies for user ID {user_id}.")
    form = AddMovieForm()
    try:
        movies = data_manager.get_user_movies(user_id)
        print(movies)
        if movies:
            logging.info(f"Found {len(movies)} movies for user ID {user_id}.")
            return render_template(
                "movies.html", movies=movies, user_id=user_id, form=form
            )
        else:
            logging.warning(f"No movies found for user ID {user_id}.")
            return render_template("movies.html", movies=[], user_id=user_id, form=form)
    except Exception as e:
        print(e)
        logging.error(f"Error fetching movies for user ID {user_id}: {e}")
        return render_template("movies.html", movies=[], user_id=user_id, form=form)


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """Route to handle adding a new movie for a user."""
    logging.info(f"Handling add_movie for user ID {user_id}.")

    form = AddMovieForm()

    if request.method == "POST":
        # Fetch data from OMDb if the user is submitting the form
        if form.validate_on_submit():
            try:
                # Add the movie to the database
                new_movie = Movie(
                    name=form.name.data,
                    director=form.director.data,
                    year=form.year.data,
                    rating=form.rating.data,
                    user_id=user_id,
                )
                db.session.add(new_movie)
                db.session.commit()

                logging.info(
                    f"Movie '{form.name.data}' added successfully for user ID {user_id}."
                )
                return redirect(url_for("user_movies", user_id=user_id))

            except Exception as e:
                logging.error(f"Error adding movie for user ID {user_id}: {e}")
                return render_template("error.html", message="Error adding movie."), 500

    return render_template("add_movie.html", user_id=user_id, form=form)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """Route to handle updating an existing movie."""
    logging.info(f"Handling update_movie for movie ID {movie_id}.")
    form = AddMovieForm()
    try:
        movie = data_manager.get_movie(movie_id)
        form = AddMovieForm(obj=movie)
        if not movie:
            logging.warning(f"Movie ID {movie_id} not found.")
            return render_template(ERROR_TEMPLATE, message="Movie not found."), 404
    except Exception as e:
        logging.error(f"Error retrieving movie ID {movie_id}: {e}")
        return render_template(ERROR_TEMPLATE, message="Error loading movie."), 500

    if request.method == "POST":
        try:
            name = request.form["name"]
            director = request.form["director"]
            year = request.form["year"]
            rating = request.form["rating"]
            data_manager.update_movie(movie_id, name, director, year, rating)
            logging.info(f"Movie ID {movie_id} updated successfully.")
            return redirect(url_for("user_movies", user_id=user_id))
        except Exception as e:
            logging.error(f"Error updating movie ID {movie_id}: {e}")
            return render_template(ERROR_TEMPLATE, message="Error updating movie."), 500

    return render_template("update_movie.html", movie=movie, user_id=user_id, form=form)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Route to delete a movie."""
    logging.info(f"Handling delete_movie for movie ID {movie_id}.")
    try:
        data_manager.delete_movie(
            movie_id
        )  # Call your data manager to delete the movie
        logging.info(f"Movie with ID {movie_id} deleted successfully.")
        return redirect(url_for("user_movies", user_id=user_id))
    except Exception as e:
        logging.error(f"Error deleting movie ID {movie_id}: {e}")
        return render_template("error.html", message="Error deleting movie."), 500


@app.route("/movie_suggestions", methods=["GET"])
def movie_suggestions():
    """AJAX route to get movie suggestions based on partial title."""
    query = request.args.get("query")
    api_key = current_app.config.get("OMDB_API_KEY")

    if not query:
        return jsonify([])  # No query, return an empty list

    url = f"http://www.omdbapi.com/?s={query}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            # Extract only titles, years, and imdbIDs from the search results
            movies = [
                {
                    "title": item["Title"],
                    "year": item["Year"],
                    "imdbID": item["imdbID"]
                }
                for item in data.get("Search", [])
            ]
            return jsonify(movies)
        else:
            return jsonify([])  # No matches found
    else:
        return jsonify([]), 500  # Internal server error if the request fails

@app.route("/movie_details", methods=["GET"])
def movie_details():
    """AJAX route to get full movie details based on imdbID."""
    imdb_id = request.args.get("imdbID")
    api_key = current_app.config.get("OMDB_API_KEY")
    
    if not imdb_id:
        return jsonify({})  # No imdbID, return an empty object

    url = f"http://www.omdbapi.com/?i={imdb_id}&plot=full&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        if data.get("Response") == "True":
            # Extract the necessary details
            movie_details = {
                'title': data.get('Title', "N/A"),
                'director': data.get('Director', "N/A"),
                'year': data.get('Year', "N/A"),
                'rating': data.get('imdbRating', "N/A")
            }
            return jsonify(movie_details)
        else:
            return jsonify({})  # Movie not found
    else:
        return jsonify({}), 500  # Internal server error if the request fails


# ----------- Error Handlers -----------


@app.errorhandler(404)
def page_not_found(e):
    """Custom handler for 404 errors."""
    logging.error("404 error: Page not found.")
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom handler for 500 errors."""
    logging.error("500 error: Internal server error.")
    return render_template("500.html"), 500


# ----------- Run the App -----------

if __name__ == "__main__":
    app.run(debug=True)
