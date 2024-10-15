# app.py

from flask import Flask, render_template, request, redirect, url_for
from models.data_manager import SQLiteDataManager as DataManager
from models import db
from models.db_models import User

app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize the data manager
db.init_app(app)
data_manager = DataManager(app)





@app.route("/users")
def list_users():
    """Route for the home page, showing the list of users."""
    users = data_manager.get_all_users()
    return render_template("users.html", users=users)


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Route to display and handle the form to add a new user."""
    if request.method == "POST":
        # Process the form and add the user
        name = request.form["name"]
                
        new_user = User(name=name)

        data_manager.add_user(new_user)
        return redirect(url_for("list_users"))  # Redirect back to the users list

    return render_template("add_user.html")

@app.route("/")
def home():
    """Route for the home page."""
    return render_template("home.html")

@app.route("/user/<int:user_id>")
def user_movies(user_id):
    """Route to display a user's movies."""
    movies = data_manager.get_user_movies(user_id)
    if movies is not None:
        return render_template("movies.html", movies=movies)
    else:
        return "User not found", 404


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """Route to display and handle the form to add a new movie."""
    if request.method == "POST":
        name = request.form["name"]
        director = request.form["director"]
        year = request.form["year"]
        rating = request.form["rating"]
        data_manager.add_movie(user_id, name, director, year, rating)
        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("add_movie.html", user_id=user_id)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=["GET", "POST"])
def update_movie(user_id, movie_id):
    """Route to display and handle the form to update a movie."""
    movie = data_manager.get_movie(movie_id)
    if request.method == "POST":
        name = request.form["name"]
        director = request.form["director"]
        year = request.form["year"]
        rating = request.form["rating"]
        data_manager.update_movie(movie_id, name, director, year, rating)
        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("update_movie.html", movie=movie, user_id=user_id)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Route to delete a movie."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)
