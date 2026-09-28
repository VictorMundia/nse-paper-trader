# This imports Blueprint to group the trade routes and jsonify to reply in JSON.
from flask import Blueprint, jsonify

# This imports jwt_required to protect routes and get_jwt_identity to read the logged-in user's ID.
from flask_jwt_extended import get_jwt_identity, jwt_required

# This reuses the safe JSON-body reader from the auth routes.
from app.routes.auth import _read_json_object

# This reuses the strict query-string number reader from the stock routes.
from app.routes.stocks import read_int_query_arg

# This imports the Trade model so we can list the student's history.
from app.models.trade import Trade

# This imports the buy and sell rules and the error type they raise.
from app.services.trading_service import TradeError, buy_shares, sell_shares

# This creates the blueprint; every route below starts with /api/trades.
trades_bp = Blueprint("trades", __name__, url_prefix="/api/trades")

# This is how many trades the history returns if the caller does not say.
DEFAULT_HISTORY_LIMIT = 50

# This is the most trades one history request may return.
MAX_HISTORY_LIMIT = 500


def _trade_to_dict(trade):
    """Build the JSON for one trade; money is sent as text to keep exact cents."""
    # This returns every field the frontend shows in the trade history table.
    return {
        "id": trade.id,
        "ticker": trade.stock.ticker,
        "company_name": trade.stock.company_name,
        "trade_type": trade.trade_type,
        "quantity": trade.quantity,
        "price_at_trade": str(trade.price_at_trade),
        "total_value": str(trade.total_value),
        "realized_pnl": str(trade.realized_pnl) if trade.realized_pnl is not None else None,
        "traded_at": trade.traded_at.isoformat(),
    }


def _execute_trade(trade_function):
    """Read {ticker, quantity}, run a buy or sell, and turn the result into an HTTP response."""
    # This reads the body, or None if it is not a JSON object.
    data = _read_json_object()
    # This rejects a missing or malformed body.
    if data is None:
        # This tells the caller what shape is expected.
        return jsonify({"message": "Request body must be a JSON object with ticker and quantity."}), 400
    # This runs the trade; validation happens inside the service.
    try:
        # The token stores the user ID as text, so it is converted back to a number.
        trade, cash_balance = trade_function(int(get_jwt_identity()), data.get("ticker"), data.get("quantity"))
    # This turns a rule violation (e.g. insufficient funds) into a friendly error.
    except TradeError as error:
        # This uses the status code chosen by the service (400, 404, or 503).
        return jsonify({"message": error.message}), error.status_code
    # This returns the executed trade and the new cash balance.
    return jsonify({"message": "Trade executed.", "trade": _trade_to_dict(trade), "cash_balance": str(cash_balance)}), 201


# This buys shares for the logged-in student.
@trades_bp.route("/buy", methods=["POST"])
@jwt_required()
def buy():
    # This delegates to the shared trade handler with the buy rule.
    return _execute_trade(buy_shares)


# This sells shares for the logged-in student.
@trades_bp.route("/sell", methods=["POST"])
@jwt_required()
def sell():
    # This delegates to the shared trade handler with the sell rule.
    return _execute_trade(sell_shares)


# This returns the logged-in student's trade history, newest first.
@trades_bp.route("", methods=["GET"])
@jwt_required()
def list_trades():
    # This reads ?limit=N; None means it was not a whole number.
    limit = read_int_query_arg("limit", DEFAULT_HISTORY_LIMIT)
    # This rejects missing, zero, negative, or too-large values.
    if limit is None or not 1 <= limit <= MAX_HISTORY_LIMIT:
        # This tells the caller the allowed range.
        return jsonify({"message": f"limit must be a whole number from 1 to {MAX_HISTORY_LIMIT}."}), 400
    # This loads only this student's trades, so no one can see anyone else's history.
    trades = (
        # This starts a query on the trades table.
        Trade.query
        # This keeps only the logged-in student's trades.
        .filter_by(user_id=int(get_jwt_identity()))
        # This puts the newest first; id breaks ties between trades in the same instant.
        .order_by(Trade.traded_at.desc(), Trade.id.desc())
        # This caps how many rows come back.
        .limit(limit)
        # This runs the query.
        .all()
    )
    # This returns the list of trades.
    return jsonify([_trade_to_dict(trade) for trade in trades]), 200
