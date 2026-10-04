# This imports Blueprint to group the route, jsonify to reply in JSON, and request to read ?level=.
from flask import Blueprint, jsonify, request

# This imports jwt_required to protect the route and get_jwt_identity to read the logged-in user's ID.
from flask_jwt_extended import get_jwt_identity, jwt_required

# This reuses the allowed experience levels from registration.
from app.routes.auth import EXPERIENCE_LEVELS

# This imports the ranking logic.
from app.services.leaderboard_service import build_leaderboard

# This creates the blueprint; the route below is /api/leaderboard.
leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/api/leaderboard")


# This returns the ranking; logged-in only, because it reflects other students' activity.
@leaderboard_bp.route("", methods=["GET"])
@jwt_required()
def get_leaderboard():
    # This reads ?level=beginner etc.; empty means everyone.
    level = (request.args.get("level") or "").strip().lower() or None
    # This rejects unknown levels.
    if level is not None and level not in EXPERIENCE_LEVELS:
        # This tells the caller the allowed values.
        return jsonify({"message": f"level must be one of: {', '.join(EXPERIENCE_LEVELS)}."}), 400
    # This builds and returns the leaderboard.
    return jsonify(build_leaderboard(int(get_jwt_identity()), level)), 200
