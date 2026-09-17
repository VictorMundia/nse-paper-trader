# This imports Flask so we can create a backend application instance.
from flask import Flask

# This imports centralized configuration settings for the app.
from app.config.settings import Config

# This imports shared extension objects used across the application.
from app.extensions import db, bcrypt, jwt

# This imports the auth blueprint so we can register authentication routes.
from app.routes.auth import auth_bp

# This defines a factory function that builds and configures the Flask app.
def create_app():
    # This creates the Flask application instance.
    app = Flask(__name__)
    # This loads configuration values into the Flask app.
    app.config.from_object(Config)
    # This attaches SQLAlchemy to the Flask app instance.
    db.init_app(app)
    # This attaches Bcrypt to the Flask app instance for password hashing.
    bcrypt.init_app(app)
    # This attaches JWT manager to the Flask app instance for token auth.
    jwt.init_app(app)
    # This imports all model classes so SQLAlchemy knows table definitions without overriding the Flask app variable.
    from app import models
    # This registers the authentication blueprint so /api/auth routes are reachable.
    app.register_blueprint(auth_bp)
    # This returns the fully configured app instance.
    return app