# This imports Flask so we can create a backend application instance.
from flask import Flask  # type: ignore[import-not-found]

# This imports centralized configuration settings for the app.
from app.config.settings import Config

# This imports the shared SQLAlchemy object used across all models.
from app.extensions import db

# This defines a factory function that builds and configures the Flask app.
def create_app():
    # This creates the Flask application instance.
    app = Flask(__name__)
    # This loads configuration values into the Flask app.
    app.config.from_object(Config)
    # This attaches SQLAlchemy to the Flask app instance.
    db.init_app(app)
    # This returns the fully configured app instance.
    return app