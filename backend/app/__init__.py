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

# This imports the watchlist blueprint for /api/watchlist.
from app.routes.watchlist import watchlist_bp

# This imports the leaderboard blueprint for /api/leaderboard.
from app.routes.leaderboard import leaderboard_bp

# These are the only websites allowed to call the API; Vite may open either address.
ALLOWED_FRONTEND_ORIGINS = [
    # The Vite dev server when opened as localhost.
    "http://localhost:5173",
    # The Vite dev server when opened as 127.0.0.1.
    "http://127.0.0.1:5173",
]

# These settings must be present in .env, or the app cannot work safely.
REQUIRED_SETTINGS = ("SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY")

# This defines a factory function that builds and configures the Flask app.
def create_app(config_overrides=None):
    # This creates the Flask application instance.
    app = Flask(__name__)
    # This loads configuration values into the Flask app.
    app.config.from_object(Config)
    # Tests pass overrides here, e.g. a separate test database, so real data is never touched.
    if config_overrides:
        # This replaces the matching settings.
        app.config.update(config_overrides)
    # This lists any required setting that is missing or empty.
    missing = [key for key in REQUIRED_SETTINGS if not app.config.get(key)]
    # Failing at startup with a clear message beats failing later with a confusing error.
    if missing:
        # SQLALCHEMY_DATABASE_URI comes from DATABASE_URL in .env, so the message names the .env key.
        names = ["DATABASE_URL" if key == "SQLALCHEMY_DATABASE_URI" else key for key in missing]
        # This stops the app from starting.
        raise RuntimeError(f"Missing required setting(s) in backend/.env: {', '.join(names)}")
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
    # This makes /api/watchlist routes reachable.
    app.register_blueprint(watchlist_bp)
    # This makes /api/leaderboard reachable.
    app.register_blueprint(leaderboard_bp)
    # This returns the fully configured app instance.
    return app