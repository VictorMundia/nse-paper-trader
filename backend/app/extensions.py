# This imports SQLAlchemy so our Flask app can talk to PostgreSQL using Python objects.
from flask_sqlalchemy import SQLAlchemy

# This creates one shared SQLAlchemy instance that all models will use later.
db = SQLAlchemy()
