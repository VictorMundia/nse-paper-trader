# This imports jsonify so the token error handlers below can reply in JSON.
from flask import jsonify

# This imports datetime tools so token issue times can be compared with password change times.
from datetime import datetime, timezone

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


# This replaces the library's reply when a request has no token at all.
@jwt.unauthorized_loader
def handle_missing_token(reason):
    # This uses the same "message" key as all our other API errors.
    return jsonify({"message": "Please log in to continue."}), 401


# This replaces the library's reply when a token is corrupted, tampered with, or malformed.
@jwt.invalid_token_loader
def handle_invalid_token(reason):
    # The library would use 422 here; 401 lets the frontend treat every auth failure the same way.
    return jsonify({"message": "Your session is invalid. Please log in again."}), 401


# This replaces the library's reply when a token is older than JWT_ACCESS_TOKEN_EXPIRES.
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    # This tells the student why they were logged out.
    return jsonify({"message": "Your session has expired. Please log in again."}), 401


# This runs on every protected request and rejects tokens issued before the user's last password change.
@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    # Imported here because models import this file, so a top-level import would be circular.
    from app.models.user import User

    # This loads the token's owner; "sub" is the user ID we stored at login.
    user = db.session.get(User, int(jwt_payload["sub"]))
    # A missing user is handled by the route (404); a user who never changed their password has nothing to revoke.
    if user is None or user.password_changed_at is None:
        # This accepts the token.
        return False
    # "iat" (issued at) is whole seconds since 1970 in UTC; converted to the same naive UTC format as the database.
    issued_at = datetime.fromtimestamp(jwt_payload["iat"], tz=timezone.utc).replace(tzinfo=None)
    # Tokens created before the change are rejected; the one issued in the same second as the change is kept.
    return issued_at < user.password_changed_at


# This replies when a token was rejected by is_token_revoked above.
@jwt.revoked_token_loader
def handle_revoked_token(jwt_header, jwt_payload):
    # This explains why the session ended.
    return jsonify({"message": "Your password was changed. Please log in again."}), 401