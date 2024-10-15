# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from models import db 


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    movies = db.relationship("Movie", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"


class Movie(db.Model):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    director =Column(String(100))
    year = Column(Integer)
    rating = Column(Float)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Movie {self.name}>"
