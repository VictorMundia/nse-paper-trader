# This imports Blueprint to group the watchlist routes and jsonify to reply in JSON.
from flask import Blueprint, jsonify

# This imports jwt_required to protect routes and get_jwt_identity to read the logged-in user's ID.
from flask_jwt_extended import get_jwt_identity, jwt_required

# This imports IntegrityError, raised if the same stock is added twice at the same moment.
from sqlalchemy.exc import IntegrityError

# This imports the shared database object.
from app.extensions import db

# This imports the models the watchlist needs.
from app.models.stock import Stock
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.watchlistitem import WatchlistItem

# This reuses the safe JSON-body reader from the auth routes.
from app.routes.auth import _read_json_object

# This reuses the stock lookup and the stock JSON shape from the stock routes.
from app.routes.stocks import _find_active_stock, _stock_summary

# This creates the blueprint; every route below starts with /api/watchlist.
watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/api/watchlist")

# The schema supports several named lists per user; the app uses one default list.
DEFAULT_WATCHLIST_NAME = "My Watchlist"


def _current_user_watchlist(create=False):
    """Return the logged-in user's default watchlist, optionally creating it on first use."""
    # The token stores the user ID as text.
    user_id = int(get_jwt_identity())
    # This finds the user's first (default) watchlist.
    watchlist = Watchlist.query.filter_by(user_id=user_id).order_by(Watchlist.id).first()
    # This creates the list the first time a student stars a stock.
    if watchlist is None and create:
        # This avoids a foreign key error if the token's user was deleted.
        if db.session.get(User, user_id) is None:
            # This signals "no such user" to the caller.
            return None
        # This builds the new list.
        watchlist = Watchlist(user_id=user_id, watchlist_name=DEFAULT_WATCHLIST_NAME)
        # This stages it.
        db.session.add(watchlist)
        # This assigns watchlist.id so items can reference it.
        db.session.flush()
    # This returns the list, or None.
    return watchlist


# This returns the stocks on the student's watchlist with their latest prices.
@watchlist_bp.route("", methods=["GET"])
@jwt_required()
def get_watchlist():
    # Reading never creates a list.
    watchlist = _current_user_watchlist()
    # No list yet means nothing is starred.
    if watchlist is None:
        # This returns an empty list.
        return jsonify([]), 200
    # This loads the starred stocks alphabetically.
    stocks = (
        # This starts from the stocks table.
        Stock.query
        # This keeps stocks that are items on this watchlist.
        .join(WatchlistItem, WatchlistItem.stock_id == Stock.id)
        # This limits to this student's list.
        .filter(WatchlistItem.watchlist_id == watchlist.id)
        # This sorts by ticker.
        .order_by(Stock.ticker)
        # This runs the query.
        .all()
    )
    # This returns each stock with its latest price.
    return jsonify([_stock_summary(stock) for stock in stocks]), 200


# This adds a stock to the watchlist.
@watchlist_bp.route("", methods=["POST"])
@jwt_required()
def add_to_watchlist():
    # This reads the body, or None if it is not a JSON object.
    data = _read_json_object()
    # This reads the ticker only if it is text.
    ticker = data.get("ticker") if data and isinstance(data.get("ticker"), str) else ""
    # This rejects a missing ticker.
    if not ticker.strip():
        # This tells the caller what is expected.
        return jsonify({"message": "ticker is required."}), 400
    # This finds the stock in any capitalisation.
    stock = _find_active_stock(ticker)
    # This handles tickers we do not track.
    if stock is None:
        # 404 means "that stock does not exist".
        return jsonify({"message": f"Stock '{ticker}' was not found."}), 404
    # This gets or creates the student's list.
    watchlist = _current_user_watchlist(create=True)
    # This handles a valid token whose user was deleted.
    if watchlist is None:
        # 404 because the account no longer exists.
        return jsonify({"message": "User not found."}), 404
    # Adding a stock that is already starred is not an error.
    if WatchlistItem.query.filter_by(watchlist_id=watchlist.id, stock_id=stock.id).first():
        # This saves a newly created list, if any, and reports success.
        db.session.commit()
        # 200 because nothing new was created.
        return jsonify({"message": f"{stock.ticker} is already on your watchlist.", "ticker": stock.ticker}), 200
    # This stages the new item.
    db.session.add(WatchlistItem(watchlist_id=watchlist.id, stock_id=stock.id))
    # The unique constraint stops duplicates if two clicks arrive at the same moment.
    try:
        # This saves the item.
        db.session.commit()
    # This handles that race.
    except IntegrityError:
        # This undoes the duplicate insert.
        db.session.rollback()
        # The stock is on the list either way.
        return jsonify({"message": f"{stock.ticker} is already on your watchlist.", "ticker": stock.ticker}), 200
    # 201 means something new was created.
    return jsonify({"message": f"{stock.ticker} added to your watchlist.", "ticker": stock.ticker}), 201


# This removes a stock from the watchlist.
@watchlist_bp.route("/<ticker>", methods=["DELETE"])
@jwt_required()
def remove_from_watchlist(ticker):
    # This finds the stock in any capitalisation.
    stock = _find_active_stock(ticker)
    # This handles tickers we do not track.
    if stock is None:
        # 404 means "that stock does not exist".
        return jsonify({"message": f"Stock '{ticker}' was not found."}), 404
    # Reading never creates a list.
    watchlist = _current_user_watchlist()
    # This deletes the item if it exists; removing something not on the list is not an error.
    if watchlist is not None:
        # This deletes the matching row, if any.
        WatchlistItem.query.filter_by(watchlist_id=watchlist.id, stock_id=stock.id).delete()
        # This saves the change.
        db.session.commit()
    # This confirms the result.
    return jsonify({"message": f"{stock.ticker} removed from your watchlist.", "ticker": stock.ticker}), 200
