# This imports datetime and timedelta so we can filter price history by date.
from datetime import datetime, timedelta

# This imports Blueprint to group the stock routes, jsonify to reply in JSON, and request to read query strings.
from flask import Blueprint, jsonify, request

# This imports the Price model so we can read price history.
from app.models.price import Price

# This imports the Stock model so we can list and look up stocks.
from app.models.stock import Stock

# This imports the money-rounding helper shared with the trading rules.
from app.services.trading_service import to_money

# This creates the blueprint; every route below starts with /api/stocks.
stocks_bp = Blueprint("stocks", __name__, url_prefix="/api/stocks")

# This is the default number of days of price history for charts.
DEFAULT_HISTORY_DAYS = 30

# This is the most history a single request may ask for.
MAX_HISTORY_DAYS = 365


def _stock_summary(stock):
    """Build the JSON for one stock: latest price and the change since the previous update."""
    # This fetches the two newest prices in one query, using the (stock_id, recorded_at) index.
    latest_two = Price.query.filter_by(stock_id=stock.id).order_by(Price.recorded_at.desc()).limit(2).all()
    # This is the newest price row, or None if the stock was never scraped.
    latest = latest_two[0] if latest_two else None
    # This is the price before it, or None if there is only one.
    previous = latest_two[1] if len(latest_two) > 1 else None
    # This is the change in KES since the previous update, if we can compute it.
    change = latest.close_price - previous.close_price if latest and previous else None
    # This is the change as a percentage; the check avoids dividing by zero.
    change_percent = to_money(change / previous.close_price * 100) if change is not None and previous.close_price else None
    # This returns the stock in a JSON-friendly shape; money is sent as text to keep exact cents.
    return {
        "ticker": stock.ticker,
        "company_name": stock.company_name,
        "sector": stock.sector,
        "price": str(latest.close_price) if latest else None,
        "previous_price": str(previous.close_price) if previous else None,
        "change": str(change) if change is not None else None,
        "change_percent": str(change_percent) if change_percent is not None else None,
        "volume": latest.volume if latest else None,
        "last_updated": latest.recorded_at.isoformat() if latest else None,
    }


def _find_active_stock(ticker):
    """Return the active stock for a ticker in any capitalisation, or None."""
    # This normalises "scom" or " SCOM " to "SCOM" before looking it up.
    return Stock.query.filter_by(ticker=ticker.strip().upper(), is_active=True).first()


def read_int_query_arg(name, default):
    """Return ?name=N as an int, the default if it is absent, or None if it is not a whole number."""
    # This reads the raw text, e.g. "30" or "abc".
    raw_value = request.args.get(name)
    # This uses the default only when the parameter is missing entirely.
    if raw_value is None:
        # This returns the default value.
        return default
    # Flask's type=int would silently fall back to the default here, hiding the caller's mistake.
    try:
        # This converts text such as "30" into the number 30.
        return int(raw_value)
    # This catches text such as "abc" or "2.5".
    except ValueError:
        # None makes the caller's range check reject the value with a 400.
        return None


# This lists every tradable stock with its latest price.
@stocks_bp.route("", methods=["GET"])
def list_stocks():
    # This loads all active stocks alphabetically by ticker.
    stocks = Stock.query.filter_by(is_active=True).order_by(Stock.ticker).all()
    # This builds a summary for each stock and returns the list.
    return jsonify([_stock_summary(stock) for stock in stocks]), 200


# This returns one stock's details.
@stocks_bp.route("/<ticker>", methods=["GET"])
def get_stock(ticker):
    # This looks up the stock.
    stock = _find_active_stock(ticker)
    # This handles tickers we do not track.
    if stock is None:
        # 404 means "that stock does not exist".
        return jsonify({"message": f"Stock '{ticker}' was not found."}), 404
    # This returns the stock summary.
    return jsonify(_stock_summary(stock)), 200


# This returns a stock's price history, oldest first, ready for a chart.
@stocks_bp.route("/<ticker>/prices", methods=["GET"])
def get_price_history(ticker):
    # This looks up the stock.
    stock = _find_active_stock(ticker)
    # This handles tickers we do not track.
    if stock is None:
        # 404 means "that stock does not exist".
        return jsonify({"message": f"Stock '{ticker}' was not found."}), 404
    # This reads ?days=N; None means it was not a whole number.
    days = read_int_query_arg("days", DEFAULT_HISTORY_DAYS)
    # This rejects missing, zero, negative, or too-large values.
    if days is None or not 1 <= days <= MAX_HISTORY_DAYS:
        # This tells the caller the allowed range.
        return jsonify({"message": f"days must be a whole number from 1 to {MAX_HISTORY_DAYS}."}), 400
    # recorded_at is stored in UTC, so the cut-off is computed in UTC too.
    since = datetime.utcnow() - timedelta(days=days)
    # This loads the stock's prices in the window, oldest first so the chart reads left to right.
    rows = (
        # This starts a query on the prices table.
        Price.query
        # This keeps only this stock's rows inside the time window.
        .filter(Price.stock_id == stock.id, Price.recorded_at >= since)
        # This sorts oldest to newest.
        .order_by(Price.recorded_at.asc())
        # This runs the query.
        .all()
    )
    # This returns the ticker, the window, and one point per price row.
    return jsonify(
        {
            "ticker": stock.ticker,
            "days": days,
            "prices": [
                {"price": str(row.close_price), "volume": row.volume, "recorded_at": row.recorded_at.isoformat()}
                for row in rows
            ],
        }
    ), 200
