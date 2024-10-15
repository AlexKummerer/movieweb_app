
from app import app
from models import db

# Use the application context to run db.create_all()
with app.app_context():
    db.create_all()  # This will create all the tables in the database