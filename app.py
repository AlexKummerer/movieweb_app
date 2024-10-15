# app.py

from flask import Flask, render_template, request, redirect, url_for
from models.data_manager import SQLiteDataManager as DataManager
from models import db

app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize the data manager
data_manager = DataManager()
db.init_app(app)


@app.route("/")
def index():
    """Route for the home page, showing the list of users."""
    users = data_manager.get_all_users()
    return render_template("index.html", users=users)


@app.route("/user/<int:user_id>")
def user_movies(user_id):
    """Route to display a user's movies."""
    movies = data_manager.get_user_movies(user_id)
    if movies is not None:
        return render_template("movies.html", movies=movies)
    else:
        return "User not found", 404


@app.route("/add_movie", methods=["POST"])
def add_movie():
    """Route to add a movie to a user's list."""
    user_id = request.form["user_id"]
    name = request.form["name"]
    director = request.form["director"]
    year = request.form["year"]
    rating = request.form["rating"]
    data_manager.add_movie(user_id, name, director, year, rating)
    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)
