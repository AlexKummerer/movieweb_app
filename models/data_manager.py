# models/sqlite_data_manager.py

from flask_sqlalchemy import SQLAlchemy
from models.data_manager_interface import DataManagerInterface
from models.db_models import db, User, Movie


class SQLiteDataManager(DataManagerInterface):
    """Concrete class implementing the DataManagerInterface for SQLite."""

    def __init__(self, db_file_name):
        """Initialize the SQLite database connection."""
        self.db = SQLAlchemy(db_file_name)

    def get_all_users(self):
        """Retrieve all users from the SQLite database."""
        return User.query.all()

    def get_user_movies(self, user_id):
        """Retrieve all movies for a given user from the SQLite database."""
        user = User.query.get(user_id)
        if user:
            return user.movies
        return None

    def add_user(self, user):
        """Add a new user to the SQLite database."""
        db.session.add(user)
        db.session.commit()
        return user

    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie to the user's movie list in the SQLite database."""
        user = User.query.get(user_id)
        if user:
            new_movie = Movie(
                name=name, director=director, year=year, rating=rating, user_id=user.id
            )
            db.session.add(new_movie)
            db.session.commit()
            return new_movie
        return None

    def update_movie(self, movie_id, name=None, director=None, year=None, rating=None):
        """Update a movie's information in the SQLite database."""
        movie = Movie.query.get(movie_id)
        if movie:
            if name:
                movie.name = name
            if director:
                movie.director = director
            if year:
                movie.year = year
            if rating:
                movie.rating = rating
            db.session.commit()
            return movie
        return None

    def delete_movie(self, movie_id):
        """Delete a movie from the SQLite database."""
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False
