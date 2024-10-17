# models/sqlite_data_manager.py

import logging
from flask_sqlalchemy import SQLAlchemy
from models.data_management_interface import DataManagerInterface
from models.db_models import db, User, Movie


class SQLiteDataManager(DataManagerInterface):
    """Concrete class implementing the DataManagerInterface for SQLite."""

    def __init__(self, app):
        """Initialize the SQLite database connection."""
        with app.app_context():
            db.create_all()

    def get_all_users(self):
        """Retrieve all users from the SQLite database."""
        return User.query.all()

    def get_user_movies(self, user_id):
        """Retrieve all movies for a given user from the SQLite database."""
        try:
            # Fetch the user by user_id using SQLAlchemy's session.get
            user = db.session.get(User, user_id)

            if user:
                logging.info(f"Fetching movies for user with ID {user_id}.")

                # Check if the user has any movies
                if user.movies:
                    logging.info(
                        f"Found user: {user.name} with {len(user.movies)} movies."
                    )
                    return user.movies
                else:
                    logging.info(f"User {user.name} has no movies.")
                    return []  # Return an empty list if there are no movies
            else:
                logging.warning(f"User with ID {user_id} not found.")
                return []  # Return an empty list if the user is not found

        except Exception as e:
            logging.error(f"Error fetching movies for user ID {user_id}: {e}")
            return []

    def add_user(self, user):
        """Add a new user to the SQLite database."""
        db.session.add(user)
        db.session.commit()
        return user


    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie to the user's movie list in the SQLite database."""
        try:
        # Fetch the user to ensure they exist
            user = db.session.get(User, user_id)

            if not user:
                logging.warning(f"User with ID {user_id} not found.")
                return None

        # Optional validation: Ensure year is an integer and rating is a float
            try:
                year = int(year)  # Ensure the year is an integer
                rating = float(rating)  # Ensure the rating is a float
            except ValueError:
                logging.error("Invalid year or rating format.")
                return None

        # Create a new movie object and associate it with the user
            new_movie = Movie(
            name=name, director=director, year=year, rating=rating, user_id=user.id
        )

        # Add the new movie to the session and commit it to the database
            db.session.add(new_movie)
            db.session.commit()

            logging.info(f"Movie '{name}' added successfully for user ID {user_id}.")
            return new_movie

        except Exception as e:
            logging.error(f"Error adding movie for user ID {user_id}: {e}")
            db.session.rollback()  # Rollback the session in case of an error
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

    def get_movie(self, movie_id):
        """Retrieve a single movie from the SQLite database."""
        return Movie.query.get(movie_id)
