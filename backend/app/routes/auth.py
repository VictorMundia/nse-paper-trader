# This imports re so we can check the email format with a pattern.
import re

# This imports Blueprint so we can group authentication routes together.
from flask import Blueprint
# This imports jsonify so we can return JSON responses to the frontend.
from flask import jsonify
# This imports request so we can read JSON sent by the frontend.
from flask import request
# This imports create_access_token so we can generate JWT tokens after successful login.
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# This imports the shared database object for saving and querying users.
from app.extensions import db
# This imports the shared bcrypt object for secure password hashing and verification.
from app.extensions import bcrypt
# This imports the User model so we can create and query user records.
from app.models.user import User
# This imports the password reset rules and the shared "save a new password" helper.
from app.services.password_reset_service import ResetTokenError, request_password_reset, reset_password_with_token, set_new_password

# This creates a blueprint named auth for all authentication endpoints.
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# This pattern means: some text, one @, some text, a dot, some text, with no spaces anywhere.
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# This matches the String(120) size of the full_name and email columns in the users table.
MAX_FIELD_LENGTH = 120
# This is the shortest name we accept.
MIN_NAME_LENGTH = 2
# This is the shortest password we accept.
MIN_PASSWORD_LENGTH = 8
# Bcrypt ignores everything after 72 bytes, so longer passwords would be silently cut.
MAX_PASSWORD_BYTES = 72
# These are the only experience levels a student can pick; they group participants for the survey analysis.
EXPERIENCE_LEVELS = ("beginner", "intermediate", "advanced")


def _read_json_object():
    """Return the request body as a dict, or None if it is missing, not JSON, or not a JSON object."""
    # silent=True returns None instead of an HTML error page when the body is not valid JSON.
    data = request.get_json(silent=True)
    # This only accepts a JSON object like {...}, not a list, number, or string.
    return data if isinstance(data, dict) else None


def _get_text(data, key):
    """Return a field as trimmed text, or an empty string if it is missing or not text."""
    # This reads the field, which could be any JSON type.
    value = data.get(key)
    # This treats numbers, lists, null, etc. as missing so the required-field check rejects them.
    return value.strip() if isinstance(value, str) else ""


def _get_password(data, key):
    """Return a password field exactly as typed (never trimmed), or "" if it is not text."""
    # Spaces can be part of a password, so they are kept.
    value = data.get(key)
    # This treats non-text values as missing.
    return value if isinstance(value, str) else ""


def _password_rule_error(password):
    """Return an error message if a new password breaks the rules, or None if it is acceptable."""
    # This rejects passwords that are too short.
    if len(password) < MIN_PASSWORD_LENGTH:
        # This tells the user the minimum password length.
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    # This measures in bytes because emoji and accented letters use more than one byte each.
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        # This tells the user the password is too long.
        return f"Password must be at most {MAX_PASSWORD_BYTES} bytes long."
    # This means the password is acceptable.
    return None

# This defines a POST route for user registration.
@auth_bp.route("/register", methods=["POST"])
def register():
    # This reads the incoming JSON body, or None if it is unusable.
    data = _read_json_object()
    # This returns a 400 error if the request body is missing or not a JSON object.
    if data is None:
        # This sends an error message to the client for a bad body.
        return jsonify({"message": "Request body must be a JSON object."}), 400
    # This reads full_name from the request as trimmed text.
    full_name = _get_text(data, "full_name")
    # This reads email as trimmed text and normalizes it to lowercase.
    email = _get_text(data, "email").lower()
    # This reads password, keeping it exactly as typed, or "" if it is not text.
    password = data.get("password") if isinstance(data.get("password"), str) else ""
    # This reads experience_level as trimmed lowercase text so "Beginner " becomes "beginner".
    experience_level = _get_text(data, "experience_level").lower()
    # This validates that full_name, email, and password are all provided.
    if not full_name or not email or not password:
        # This sends an error message if required fields are missing.
        return jsonify({"message": "full_name, email, and password are required."}), 400
    # This rejects names that are too short or too long for the database column.
    if not MIN_NAME_LENGTH <= len(full_name) <= MAX_FIELD_LENGTH:
        # This tells the user the allowed name length.
        return jsonify({"message": f"full_name must be {MIN_NAME_LENGTH}-{MAX_FIELD_LENGTH} characters."}), 400
    # This rejects emails that are too long or do not look like name@domain.tld.
    if len(email) > MAX_FIELD_LENGTH or not EMAIL_PATTERN.match(email):
        # This tells the user the email is not valid.
        return jsonify({"message": "Please enter a valid email address."}), 400
    # This rejects passwords that break the length rules.
    password_error = _password_rule_error(password)
    # This returns the specific rule that was broken.
    if password_error:
        # This tells the user what to fix.
        return jsonify({"message": password_error}), 400
    # This rejects a missing experience level or one that is not on the allowed list.
    if experience_level not in EXPERIENCE_LEVELS:
        # This tells the user which values are allowed.
        return jsonify({"message": f"experience_level must be one of: {', '.join(EXPERIENCE_LEVELS)}."}), 400
    # This checks whether a user with the same email already exists.
    existing_user = User.query.filter_by(email=email).first()
    # This blocks duplicate registration if email is already in use.
    if existing_user:
        # This sends a conflict response for duplicate email.
        return jsonify({"message": "Email is already registered."}), 409
    # This hashes the plain-text password securely using bcrypt.
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    # This creates a new User object with sanitized values and hashed password.
    new_user = User(
        # This stores the validated name.
        full_name=full_name,
        # This stores the validated lowercase email.
        email=email,
        # This stores only the bcrypt hash, never the plain password.
        password_hash=password_hash,
        # This stores the validated experience level.
        experience_level=experience_level,
    )
    # This adds the new user object to the current database session.
    db.session.add(new_user)
    # This commits the session so the new user row is written to PostgreSQL.
    db.session.commit()
    # This returns a success response after user creation.
    return jsonify(
        {
            "message": "User registered successfully.",
            "user_id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "experience_level": new_user.experience_level,
            "virtual_balance": str(new_user.virtual_balance),
        }
    ), 201

# This defines a POST route for user login.
@auth_bp.route("/login", methods=["POST"])
def login():
    # This reads the incoming JSON body, or None if it is unusable.
    data = _read_json_object()
    # This returns a 400 error if the request body is missing or not a JSON object.
    if data is None:
        # This sends an error message to the client for a bad body.
        return jsonify({"message": "Request body must be a JSON object."}), 400
    # This reads email as trimmed text and normalizes it to lowercase.
    email = _get_text(data, "email").lower()
    # This reads password, keeping it exactly as typed, or "" if it is not text.
    password = data.get("password") if isinstance(data.get("password"), str) else ""
    # This validates that email and password are provided.
    if not email or not password:
        # This sends an error message if required fields are missing.
        return jsonify({"message": "email and password are required."}), 400
    # This fetches the user row matching the provided email.
    user = User.query.filter_by(email=email).first()
    # This checks whether user exists and password matches the stored bcrypt hash.
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        # This returns a generic error so attackers cannot learn which field was wrong.
        return jsonify({"message": "Invalid email or password."}), 401
    # This generates a JWT access token whose identity is the user ID.
    access_token = create_access_token(identity=str(user.id))
    # This returns login success details and the token to the frontend.
    return jsonify(
        {
            "message": "Login successful.",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "experience_level": user.experience_level,
                "virtual_balance": str(user.virtual_balance),
            },
        }
    ), 200

# This defines a protected GET route that only works with a valid JWT token.
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    # This reads the user ID stored inside the JWT token; we saved it as text at login.
    current_user_id = get_jwt_identity()
    # This loads the user's current row, converting the text ID back to a number.
    user = db.session.get(User, int(current_user_id))
    # This handles a valid token whose user has since been deleted.
    if user is None:
        # This tells the frontend the account no longer exists.
        return jsonify({"message": "User not found."}), 404
    # This returns the profile the frontend needs, never including the password hash.
    return jsonify(
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "experience_level": user.experience_level,
            # This sends money as text so the frontend never loses decimal precision.
            "virtual_balance": str(user.virtual_balance),
            # This sends the date in the standard ISO 8601 format, e.g. 2026-09-28T03:00:32.
            "created_at": user.created_at.isoformat(),
        }
    ), 200


# This lets a logged-in student change their password by proving they know the current one.
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    # This reads the body, or None if it is not a JSON object.
    data = _read_json_object()
    # This rejects a missing or malformed body.
    if data is None:
        # This tells the caller what is expected.
        return jsonify({"message": "Request body must be a JSON object."}), 400
    # This reads the current password exactly as typed.
    current_password = _get_password(data, "current_password")
    # This reads the new password exactly as typed.
    new_password = _get_password(data, "new_password")
    # This requires both fields.
    if not current_password or not new_password:
        # This tells the user what is missing.
        return jsonify({"message": "current_password and new_password are required."}), 400
    # This loads the logged-in student.
    user = db.session.get(User, int(get_jwt_identity()))
    # This handles a valid token whose user was deleted.
    if user is None:
        # 404 because the account no longer exists.
        return jsonify({"message": "User not found."}), 404
    # 400, not 401: a 401 would make the frontend log the student out for a typo.
    if not bcrypt.check_password_hash(user.password_hash, current_password):
        # This tells the student the current password is wrong.
        return jsonify({"message": "Current password is incorrect."}), 400
    # This applies the same length rules as registration.
    password_error = _password_rule_error(new_password)
    # This returns the specific rule that was broken.
    if password_error:
        # This tells the user what to fix.
        return jsonify({"message": password_error}), 400
    # This stops "changing" to the same password.
    if bcrypt.check_password_hash(user.password_hash, new_password):
        # This asks for a different password.
        return jsonify({"message": "New password must be different from your current password."}), 400
    # This saves the new hash and invalidates every older login token, including on other devices.
    set_new_password(user, new_password)
    # This writes the change to PostgreSQL.
    db.session.commit()
    # This issues a fresh token so the student stays logged in on this device.
    return jsonify({"message": "Password changed successfully.", "access_token": create_access_token(identity=str(user.id))}), 200


# This starts the "forgot password" flow by emailing a reset link.
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    # This reads the body, or None if it is not a JSON object.
    data = _read_json_object()
    # This rejects a missing or malformed body; that reveals nothing about any account.
    if data is None:
        # This tells the caller what is expected.
        return jsonify({"message": "Request body must be a JSON object."}), 400
    # This reads and normalises the email the same way registration does.
    email = _get_text(data, "email").lower()
    # This only looks up emails that could be valid.
    if EMAIL_PATTERN.match(email):
        # This emails a link if the account exists; it does nothing if it does not.
        request_password_reset(email)
    # This reply is identical whether or not the email is registered, so accounts cannot be discovered.
    return jsonify({"message": "If that email is registered, a password reset link has been sent. It expires in 30 minutes."}), 200


# This finishes the "forgot password" flow: it checks the link and saves the new password.
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    # This reads the body, or None if it is not a JSON object.
    data = _read_json_object()
    # This rejects a missing or malformed body.
    if data is None:
        # This tells the caller what is expected.
        return jsonify({"message": "Request body must be a JSON object."}), 400
    # This reads the token from the reset link.
    token = _get_text(data, "token")
    # This reads the new password exactly as typed.
    new_password = _get_password(data, "new_password")
    # This requires both fields.
    if not token or not new_password:
        # This tells the user what is missing.
        return jsonify({"message": "token and new_password are required."}), 400
    # This applies the same length rules as registration.
    password_error = _password_rule_error(new_password)
    # This returns the specific rule that was broken.
    if password_error:
        # This tells the user what to fix.
        return jsonify({"message": password_error}), 400
    # This checks the link and saves the new password.
    try:
        # This is single-use and logs out every existing session.
        reset_password_with_token(token, new_password)
    # This handles an unknown, used, or expired link.
    except ResetTokenError as error:
        # This tells the student to request a new link.
        return jsonify({"message": str(error)}), 400
    # This confirms success.
    return jsonify({"message": "Your password has been reset. You can now log in."}), 200