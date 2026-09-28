# This imports Blueprint to group the portfolio route and jsonify to reply in JSON.
from flask import Blueprint, jsonify

# This imports jwt_required to protect the route and get_jwt_identity to read the logged-in user's ID.
from flask_jwt_extended import get_jwt_identity, jwt_required

# This imports the portfolio valuation rule and the error type it raises.
from app.services.trading_service import TradeError, get_portfolio_summary

# This creates the blueprint; the route below is /api/portfolio.
portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")


# This returns the logged-in student's holdings, cash, and overall performance.
@portfolio_bp.route("", methods=["GET"])
@jwt_required()
def get_portfolio():
    # This values the portfolio at the latest prices.
    try:
        # The token stores the user ID as text, so it is converted back to a number.
        summary = get_portfolio_summary(int(get_jwt_identity()))
    # This handles a valid token whose user was deleted.
    except TradeError as error:
        # This uses the status code chosen by the service.
        return jsonify({"message": error.message}), error.status_code
    # This returns the summary.
    return jsonify(summary), 200
