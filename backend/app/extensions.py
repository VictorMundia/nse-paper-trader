# This imports SQLAlchemy so our Flask app can use ORM database access.
from flask_sqlalchemy import SQLAlchemy  # type: ignore[import-not-found]

# This imports Bcrypt so we can hash passwords securely before storing them.
from flask_bcrypt import Bcrypt  # type: ignore[import-not-found]

# This imports JWTManager so we can issue and validate login tokens.
from flask_jwt_extended import JWTManager  # type: ignore[import-not-found]

# This creates one shared SQLAlchemy instance for all database models.
db = SQLAlchemy()

# This creates one shared Bcrypt instance for password hashing operations.
bcrypt = Bcrypt()

# This creates one shared JWT manager instance for token-based authentication.
jwt = JWTManager()