from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    """Abstract base class for a DataManager."""

    @abstractmethod
    def get_all_users(self):
        """Retrieve all users."""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Retrieve all movies for a given user."""
        pass

    @abstractmethod
    def add_movie(self, user_id, name, director, year, rating):
        """Add a new movie to the user's movie list."""
        pass

    @abstractmethod
    def update_movie(self, movie_id, name=None, director=None, year=None, rating=None):
        """Update a movie's information."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete a movie from the user's list."""
        pass
    
    @abstractmethod
    def get_movie(self, movie_id):
        """Retrieve a single movie."""
        pass
