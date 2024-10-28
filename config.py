import os
from dotenv import load_dotenv

load_dotenv()


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI =  os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "data/movies.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OMDB_API_KEY = os.environ.get("OMDB_API_KEY") or "your-omdb"   
