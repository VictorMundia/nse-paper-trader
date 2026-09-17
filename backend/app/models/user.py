# This imports datetime so we can store the time when a user account is created.
from datetime import datetime

# This imports the shared SQLAlchemy database object used by all models.
from app.extensions import db

# This class defines the structure of the users table in PostgreSQL.
class User(db.Model):
    # This sets the exact table name in the database.
    __tablename__ = "users"
    # This creates the primary key column for unique user IDs.
    id = db.Column(db.Integer, primary_key=True)
    # This stores the user's full name and makes it required.
    full_name = db.Column(db.String(120), nullable=False)
    # This stores the user's email, enforces uniqueness, and makes it required.
    email = db.Column(db.String(120), unique=True, nullable=False)
    # This stores the securely hashed password string and makes it required.
    password_hash = db.Column(db.String(255), nullable=False)
    # This stores virtual balance as precise currency with a default of KES 100000.00.
    virtual_balance = db.Column(db.Numeric(12, 2), nullable=False, default=100000.00)
    # This stores the user's investing experience level and allows it to be optional.
    experience_level = db.Column(db.String(20), nullable=True)
    # This stores the UTC timestamp for when the user was created.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        # This creates a one-to-many relationship from a user to their orders.
    orders = db.relationship("Order", backref="user", lazy=True)
    # This creates a one-to-many relationship from a user to their executed trades.
    trades = db.relationship("Trade", backref="user", lazy=True)
    # This creates a one-to-many relationship from a user to their portfolio position rows.
    portfolios = db.relationship("Portfolio", backref="user", lazy=True)
    # This creates a one-to-many relationship from a user to their watchlists.
    watchlists = db.relationship("Watchlist", backref="user", lazy=True)
    # This creates a one-to-one style relationship from a user to their optional profile row.
    profile = db.relationship("UserProfile", backref="user", uselist=False, lazy=True)
    # This creates a one-to-many relationship from a user to role assignments in the junction table.
    role_assignments = db.relationship("UserRole", backref="user", lazy=True)