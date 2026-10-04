# This imports Decimal so all money maths stays exact.
from decimal import Decimal

# This imports current_app so we can read the starting balance.
from flask import current_app

# This imports the shared database object.
from app.extensions import db

# This imports the models the leaderboard reads.
from app.models.portfolio import Portfolio
from app.models.price import Price
from app.models.trade import Trade
from app.models.user import User

# This imports the money-rounding helper.
from app.services.trading_service import to_money

# This is how many students the leaderboard lists.
LEADERBOARD_SIZE = 50


def display_name(full_name):
    """Shorten a name to first name + last initial, e.g. "Victor Mundia" -> "Victor M.", to protect privacy."""
    # This splits the name into words.
    parts = full_name.split()
    # A one-word name is shown as it is.
    if len(parts) < 2:
        # This returns the single name.
        return full_name
    # This keeps the first name and the first letter of the last name.
    return f"{parts[0]} {parts[-1][0].upper()}."


def _latest_prices():
    """Return {stock_id: latest close price} using one query instead of one per stock."""
    # DISTINCT ON (PostgreSQL) keeps the first row per stock; ordering newest first makes that the latest price.
    rows = (
        # This selects the stock and its price.
        db.session.query(Price.stock_id, Price.close_price)
        # This keeps one row per stock.
        .distinct(Price.stock_id)
        # This puts each stock's newest price first.
        .order_by(Price.stock_id, Price.recorded_at.desc())
        # This runs the query.
        .all()
    )
    # This turns the rows into a lookup dictionary.
    return {stock_id: price for stock_id, price in rows}


def build_leaderboard(current_user_id, level=None):
    """Rank students who have traded by total account value; optionally only one experience level."""
    # This loads every stock's latest price once.
    prices = _latest_prices()
    # This counts trades per user in one grouped query.
    trade_counts = dict(db.session.query(Trade.user_id, db.func.count(Trade.id)).group_by(Trade.user_id).all())
    # This will hold each user's share value.
    holdings_value = {}
    # This values every holding at the latest price.
    for holding in Portfolio.query.filter(Portfolio.shares_held > 0).all():
        # This uses the latest price, or the buy price if a stock was somehow never priced.
        price = prices.get(holding.stock_id, holding.average_buy_price)
        # This adds the holding's value to the user's total.
        holdings_value[holding.user_id] = holdings_value.get(holding.user_id, Decimal("0")) + price * holding.shares_held
    # This reads the KES 100,000 starting balance.
    starting_balance = to_money(current_app.config["STARTING_VIRTUAL_BALANCE"])
    # This starts from all users, optionally narrowed to one experience level.
    users_query = User.query if level is None else User.query.filter_by(experience_level=level)
    # This will hold one entry per ranked student.
    entries = []
    # This builds an entry for each student who has traded.
    for user in users_query.all():
        # Students who never traded would all tie at the starting balance, so they are not ranked.
        if trade_counts.get(user.id, 0) == 0:
            # This skips them.
            continue
        # Total value = cash + shares at today's prices.
        total_value = to_money(user.virtual_balance + holdings_value.get(user.id, Decimal("0")))
        # This is the gain or loss since the start.
        total_return = total_value - starting_balance
        # This stores the entry; money is kept as Decimal until the JSON step.
        entries.append(
            {
                "user_id": user.id,
                "display_name": display_name(user.full_name),
                "experience_level": user.experience_level,
                "total_value": total_value,
                "total_return": total_return,
                "total_return_percent": to_money(total_return / starting_balance * 100),
                "trade_count": trade_counts[user.id],
                "is_current_user": user.id == current_user_id,
            }
        )
    # This sorts richest first; ties are broken by fewer trades, then by user ID so the order is stable.
    entries.sort(key=lambda entry: (-entry["total_value"], entry["trade_count"], entry["user_id"]))
    # This assigns ranks where equal values share a rank, e.g. 1, 2, 2, 4.
    for index, entry in enumerate(entries):
        # Same value as the previous student means same rank; otherwise rank = position.
        entry["rank"] = entries[index - 1]["rank"] if index and entry["total_value"] == entries[index - 1]["total_value"] else index + 1
    # This finds the logged-in student's own entry, which may be outside the top 50.
    you = next((entry for entry in entries if entry["is_current_user"]), None)
    # This converts an entry to JSON-friendly values and drops the internal user ID.
    def to_json(entry):
        # This copies every field except user_id.
        result = {key: value for key, value in entry.items() if key != "user_id"}
        # This sends money as text to keep exact cents.
        for key in ("total_value", "total_return", "total_return_percent"):
            # This converts Decimal to text.
            result[key] = str(result[key])
        # This returns the safe version.
        return result
    # This returns the top 50, the student's own row, and the count.
    return {
        "entries": [to_json(entry) for entry in entries[:LEADERBOARD_SIZE]],
        "you": to_json(you) if you else None,
        "ranked_count": len(entries),
        "level": level,
    }
