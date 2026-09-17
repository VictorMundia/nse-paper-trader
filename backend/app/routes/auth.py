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

# This creates a blueprint named auth for all authentication endpoints.
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# This defines a POST route for user registration.
@auth_bp.route("/register", methods=["POST"])
def register():
    # This reads the incoming JSON body from the request.
    data = request.get_json()
    # This returns a 400 error if the request body is missing.
    if not data:
        # This sends an error message to the client for missing JSON.
        return jsonify({"message": "Request body is required."}), 400
    # This reads full_name from the request and removes extra surrounding spaces.
    full_name = data.get("full_name", "").strip()
    # This reads email from the request, removes extra spaces, and normalizes to lowercase.
    email = data.get("email", "").strip().lower()
    # This reads password from the request and keeps it as entered.
    password = data.get("password", "")
    # This validates that full_name, email, and password are all provided.
    if not full_name or not email or not password:
        # This sends an error message if required fields are missing.
        return jsonify({"message": "full_name, email, and password are required."}), 400
    # This checks whether a user with the same email already exists.
    existing_user = User.query.filter_by(email=email).first()
    # This blocks duplicate registration if email is already in use.
    if existing_user:
        # This sends a conflict response for duplicate email.
        return jsonify({"message": "Email is already registered."}), 409
    # This hashes the plain-text password securely using bcrypt.
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    # This creates a new User object with sanitized values and hashed password.
    new_user = User(full_name=full_name, email=email, password_hash=password_hash)
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
            "virtual_balance": str(new_user.virtual_balance),
        }
    ), 201

# This defines a POST route for user login.
@auth_bp.route("/login", methods=["POST"])
def login():
    # This reads the incoming JSON body from the request.
    data = request.get_json()
    # This returns a 400 error if the request body is missing.
    if not data:
        # This sends an error message to the client for missing JSON.
        return jsonify({"message": "Request body is required."}), 400
    # This reads email from the request, removes extra spaces, and normalizes to lowercase.
    email = data.get("email", "").strip().lower()
    # This reads password from the request.
    password = data.get("password", "")
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
                "virtual_balance": str(user.virtual_balance),
            },
        }
    ), 200
# This imports jwt_required to protect routes and get_jwt_identity to read user identity from token.
from flask_jwt_extended import jwt_required, get_jwt_identity

# This defines a protected GET route that only works with a valid JWT token.
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    # This reads the authenticated user identity stored inside the JWT token.
    current_user_id = get_jwt_identity()
    # This returns the user identity from the token so we can verify protection works.
    return jsonify({"message": "Token is valid.", "user_id": current_user_id}), 200