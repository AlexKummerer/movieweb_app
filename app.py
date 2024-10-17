from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from forms.add_movie_form import AddMovieForm
from models.data_manager import SQLiteDataManager as DataManager
from models import db
from models.db_models import User
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
app.config.from_object("config.Config")
csrf = CSRFProtect(app)

# Initialize the data manager and the database
db.init_app(app)
data_manager = DataManager(app)


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
    try:
        movies = data_manager.get_user_movies(user_id)
        print(movies)
        if movies:
            logging.info(f"Found {len(movies)} movies for user ID {user_id}.")
            return render_template("movies.html", movies=movies, user_id=user_id)
        else:
            logging.warning(f"No movies found for user ID {user_id}.")
            return render_template("movies.html", movies=[], user_id=user_id)
    except Exception as e:
        print(e)
        logging.error(f"Error fetching movies for user ID {user_id}: {e}")
        return render_template("movies.html", movies=[], user_id=user_id)


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """Route to handle adding a new movie for a user."""
    logging.info(f"Handling add_movie for user ID {user_id}.")

    form: AddMovieForm = AddMovieForm()  # Create form instance

    if request.method == "POST" and form.validate_on_submit():
        try:
            # Extract data from form
            name = form.name.data
            director = form.director.data
            year = form.year.data
            rating = form.rating.data

            logging.info(
                f"Adding movie with data: Name: {name}, Director: {director}, Year: {year}, Rating: {rating}"
            )

            # Add movie through data_manager
            data_manager.add_movie(user_id, name, director, year, rating)
            logging.info(f"Movie '{name}' added successfully for user ID {user_id}.")

            return redirect(url_for("user_movies", user_id=user_id))

        except Exception as e:
            logging.error(f"Error adding movie for user ID {user_id}: {e}")
            return render_template(ERROR_TEMPLATE, message="Error adding movie."), 500

    return render_template("add_movie.html", user_id=user_id, form=form)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """Route to handle updating an existing movie."""
    logging.info(f"Handling update_movie for movie ID {movie_id}.")
    try:
        movie = data_manager.get_movie(movie_id)
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

    return render_template("update_movie.html", movie=movie, user_id=user_id)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Route to handle deleting a movie."""
    logging.info(f"Handling delete_movie for movie ID {movie_id}.")
    try:
        data_manager.delete_movie(movie_id)
        logging.info(f"Movie ID {movie_id} deleted successfully.")
        return redirect(url_for("user_movies", user_id=user_id))
    except Exception as e:
        logging.error(f"Error deleting movie ID {movie_id}: {e}")
        return render_template(ERROR_TEMPLATE, message="Error deleting movie."), 500


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
