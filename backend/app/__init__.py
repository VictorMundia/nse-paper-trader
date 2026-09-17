# This imports Flask so we can create our backend web application instance.
from flask import Flask  # type: ignore[import-not-found]

# This imports the Config class so the app can load settings like database URL and JWT secret.
from app.config.settings import Config

# This imports the shared SQLAlchemy object that will connect models to the Flask app.
from app.extensions import db

# This defines a function that creates and configures a Flask app instance.
def create_app():
    # This creates the Flask app and uses __name__ so Flask can locate resources correctly.
    app = Flask(__name__)
    # This loads all configuration values from the Config class into the app.
    app.config.from_object(Config)
    # This attaches the shared SQLAlchemy object to this app instance.
    db.init_app(app)
    # This returns the fully configured app so it can be used by the run/entry file.
    return app