# This imports Flask so we can create a backend application instance.
from flask import Flask

# This imports CORS so the React frontend on another port is allowed to call this API.
from flask_cors import CORS

# This imports centralized configuration settings for the app.
from app.config.settings import Config

# This imports shared extension objects used across the application.
from app.extensions import db, bcrypt, jwt

# This imports the auth blueprint so we can register authentication routes.
from app.routes.auth import auth_bp

# This imports the portfolio blueprint for /api/portfolio.
from app.routes.portfolio import portfolio_bp

# This imports the stocks blueprint for /api/stocks.
from app.routes.stocks import stocks_bp

# This imports the trades blueprint for /api/trades.
from app.routes.trades import trades_bp

# These are the only websites allowed to call the API; Vite may open either address.
ALLOWED_FRONTEND_ORIGINS = [
    # The Vite dev server when opened as localhost.
    "http://localhost:5173",
    # The Vite dev server when opened as 127.0.0.1.
    "http://127.0.0.1:5173",
]

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
    # This allows only our frontend origins to call /api/* routes from the browser.
    CORS(app, resources={r"/api/*": {"origins": ALLOWED_FRONTEND_ORIGINS}})
    # This imports all model classes so SQLAlchemy knows table definitions without overriding the Flask app variable.
    from app import models
    # This registers the authentication blueprint so /api/auth routes are reachable.
    app.register_blueprint(auth_bp)
    # This makes /api/stocks routes reachable.
    app.register_blueprint(stocks_bp)
    # This makes /api/trades routes reachable.
    app.register_blueprint(trades_bp)
    # This makes /api/portfolio reachable.
    app.register_blueprint(portfolio_bp)
    # This returns the fully configured app instance.
    return app