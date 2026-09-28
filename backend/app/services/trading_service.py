# This imports Decimal so all money maths stays exact to the cent.
from decimal import Decimal, ROUND_HALF_UP

# This imports current_app so we can read the starting balance from the app config.
from flask import current_app

# This imports the shared database object for queries, locks, and commits.
from app.extensions import db

# This imports the Portfolio model, which holds one row per stock a user owns.
from app.models.portfolio import Portfolio

# This imports the Price model so we can find each stock's latest price.
from app.models.price import Price

# This imports the Stock model so we can look up stocks by ticker.
from app.models.stock import Stock

# This imports the Trade model so every buy and sell is recorded.
from app.models.trade import Trade

# This imports the User model so we can read and update the cash balance.
from app.models.user import User

# This is one cent, used to round every money value to 2 decimal places.
CENT = Decimal("0.01")

# This caps a single order so a typo like 10000000 cannot create absurd numbers.
MAX_QUANTITY_PER_TRADE = 1_000_000


class TradeError(Exception):
    """A trade the user asked for cannot be done; carries a friendly message and an HTTP status."""

    def __init__(self, message, status_code=400):
        # This stores the message through the normal Exception mechanism.
        super().__init__(message)
        # This keeps the message so the route can send it to the frontend.
        self.message = message
        # This keeps the HTTP status code the route should return.
        self.status_code = status_code


def to_money(value):
    """Round a Decimal to 2 decimal places, the way money is shown."""
    # ROUND_HALF_UP is the rounding taught in school: 0.005 becomes 0.01.
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def get_latest_price(stock_id):
    """Return the newest Price row for a stock, or None if it has never been priced."""
    # This uses the (stock_id, recorded_at) index to jump straight to the newest row.
    return Price.query.filter_by(stock_id=stock_id).order_by(Price.recorded_at.desc()).first()


def _validate_quantity(quantity):
    """Make sure quantity is a whole number of shares within the allowed range."""
    # bool is a subclass of int in Python, so True would otherwise count as 1 share.
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        # This rejects decimals, text, lists, null, and booleans.
        raise TradeError("quantity must be a whole number of shares.")
    # This rejects zero, negatives, and absurdly large orders.
    if not 1 <= quantity <= MAX_QUANTITY_PER_TRADE:
        # This tells the user the allowed range.
        raise TradeError(f"quantity must be between 1 and {MAX_QUANTITY_PER_TRADE:,}.")


def _load_trade_context(user_id, ticker, quantity):
    """Validate inputs and return the locked user, the stock, and its latest price."""
    # This checks the quantity before touching the database.
    _validate_quantity(quantity)
    # This rejects a missing or non-text ticker.
    if not isinstance(ticker, str) or not ticker.strip():
        # This tells the user the ticker is required.
        raise TradeError("ticker is required.")
    # This finds the stock, accepting any capitalisation such as "scom".
    stock = Stock.query.filter_by(ticker=ticker.strip().upper(), is_active=True).first()
    # This handles tickers we do not track.
    if stock is None:
        # 404 means "that thing does not exist".
        raise TradeError(f"Stock '{ticker}' was not found.", 404)
    # This gets the price the trade will execute at.
    latest_price = get_latest_price(stock.id)
    # This handles a stock that has never been scraped.
    if latest_price is None:
        # 503 means "temporarily unavailable"; the next scrape will fix it.
        raise TradeError(f"No price is available for {stock.ticker} yet.", 503)
    # FOR UPDATE locks this user's row until commit, so two simultaneous trades cannot both spend the same cash.
    user = db.session.query(User).filter_by(id=user_id).with_for_update().first()
    # This handles a valid token whose user was deleted.
    if user is None:
        # 404 because the account no longer exists.
        raise TradeError("User not found.", 404)
    # This returns everything the buy or sell function needs.
    return user, stock, latest_price.close_price


def _locked_holding(user_id, stock_id):
    """Return this user's portfolio row for a stock, locked for update, or None."""
    # This locks the holding row too so share counts cannot be changed twice at once.
    return (
        # This starts a query on the portfolio table.
        db.session.query(Portfolio)
        # This picks the one row for this user and this stock.
        .filter_by(user_id=user_id, stock_id=stock_id)
        # This locks the row until commit.
        .with_for_update()
        # This returns the row or None.
        .first()
    )


def buy_shares(user_id, ticker, quantity):
    """Buy shares at the latest price. Returns (trade, new_cash_balance)."""
    # This wraps the whole trade so any failure undoes every change and releases the locks.
    try:
        # This validates inputs, finds the stock and price, and locks the user.
        user, stock, price = _load_trade_context(user_id, ticker, quantity)
        # This is what the student pays: price times number of shares.
        total_cost = to_money(price * quantity)
        # This blocks buying with money the student does not have.
        if user.virtual_balance < total_cost:
            # This tells the student exactly how short they are.
            raise TradeError(
                f"Insufficient funds: this trade costs KES {total_cost:,}, you have KES {user.virtual_balance:,}."
            )
        # This finds the existing holding for this stock, if any.
        holding = _locked_holding(user.id, stock.id)
        # This creates a holding the first time the student buys this stock.
        if holding is None:
            # This starts the holding at zero shares so the average-price maths below works.
            holding = Portfolio(user_id=user.id, stock_id=stock.id, shares_held=0, average_buy_price=Decimal("0"))
            # This stages the new holding for insertion.
            db.session.add(holding)
        # This is how much the student had already paid for their existing shares of this stock.
        previous_cost = holding.average_buy_price * holding.shares_held
        # This is the new total number of shares.
        new_share_count = holding.shares_held + quantity
        # Weighted average: (old cost + new cost) / total shares.
        holding.average_buy_price = to_money((previous_cost + total_cost) / new_share_count)
        # This stores the new share count.
        holding.shares_held = new_share_count
        # This takes the cost out of the student's cash.
        user.virtual_balance = to_money(user.virtual_balance - total_cost)
        # This records the trade for history and the leaderboard.
        trade = Trade(
            # This links the trade to the student.
            user_id=user.id,
            # This links the trade to the stock.
            stock_id=stock.id,
            # This marks it as a purchase.
            trade_type="BUY",
            # This stores how many shares were bought.
            quantity=quantity,
            # This stores the price each share was bought at.
            price_at_trade=price,
            # This stores the total paid.
            total_value=total_cost,
            # Profit or loss is only realised when selling, so it is empty for a buy.
            realized_pnl=None,
        )
        # This stages the trade row.
        db.session.add(trade)
        # This saves balance, holding, and trade together, then releases the locks.
        db.session.commit()
        # This returns the trade and the updated cash balance.
        return trade, user.virtual_balance
    # This catches every error, including our own TradeError.
    except Exception:
        # This undoes all staged changes and releases the row locks.
        db.session.rollback()
        # This passes the error on to the route unchanged.
        raise


def sell_shares(user_id, ticker, quantity):
    """Sell shares at the latest price. Returns (trade, new_cash_balance)."""
    # This wraps the whole trade so any failure undoes every change and releases the locks.
    try:
        # This validates inputs, finds the stock and price, and locks the user.
        user, stock, price = _load_trade_context(user_id, ticker, quantity)
        # This finds and locks the student's holding of this stock.
        holding = _locked_holding(user.id, stock.id)
        # This is how many shares the student owns (0 if no holding).
        shares_owned = holding.shares_held if holding else 0
        # This blocks selling shares the student does not own (no short selling).
        if shares_owned < quantity:
            # This tells the student how many they can sell.
            raise TradeError(f"You only hold {shares_owned} shares of {stock.ticker}.")
        # This is what the student receives: price times number of shares.
        proceeds = to_money(price * quantity)
        # Realised profit/loss = (sell price - average buy price) x shares sold.
        realized_pnl = to_money((price - holding.average_buy_price) * quantity)
        # This reduces the share count.
        holding.shares_held = shares_owned - quantity
        # This removes the holding completely once every share is sold.
        if holding.shares_held == 0:
            # This deletes the empty portfolio row.
            db.session.delete(holding)
        # This adds the sale proceeds to the student's cash.
        user.virtual_balance = to_money(user.virtual_balance + proceeds)
        # This records the trade for history and the leaderboard.
        trade = Trade(
            # This links the trade to the student.
            user_id=user.id,
            # This links the trade to the stock.
            stock_id=stock.id,
            # This marks it as a sale.
            trade_type="SELL",
            # This stores how many shares were sold.
            quantity=quantity,
            # This stores the price each share was sold at.
            price_at_trade=price,
            # This stores the total received.
            total_value=proceeds,
            # This stores the profit (positive) or loss (negative) on this sale.
            realized_pnl=realized_pnl,
        )
        # This stages the trade row.
        db.session.add(trade)
        # This saves balance, holding, and trade together, then releases the locks.
        db.session.commit()
        # This returns the trade and the updated cash balance.
        return trade, user.virtual_balance
    # This catches every error, including our own TradeError.
    except Exception:
        # This undoes all staged changes and releases the row locks.
        db.session.rollback()
        # This passes the error on to the route unchanged.
        raise


def get_portfolio_summary(user_id):
    """Return the student's holdings valued at the latest prices, plus cash and overall totals."""
    # This loads the student so we can read their cash balance.
    user = db.session.get(User, user_id)
    # This handles a valid token whose user was deleted.
    if user is None:
        # 404 because the account no longer exists.
        raise TradeError("User not found.", 404)
    # This loads every stock the student owns, alphabetically by ticker.
    holdings = (
        # This starts a query on the portfolio table.
        Portfolio.query
        # This joins stocks so we can sort by ticker.
        .join(Stock, Portfolio.stock_id == Stock.id)
        # This keeps only this student's rows that still have shares.
        .filter(Portfolio.user_id == user.id, Portfolio.shares_held > 0)
        # This sorts alphabetically.
        .order_by(Stock.ticker)
        # This runs the query.
        .all()
    )
    # This will hold one dictionary per holding.
    positions = []
    # This adds up the market value of all holdings.
    holdings_value = Decimal("0")
    # This adds up what the student paid for all current holdings.
    holdings_cost = Decimal("0")
    # This values each holding.
    for holding in holdings:
        # This gets the latest price for this stock.
        latest = get_latest_price(holding.stock_id)
        # This uses the average buy price if the stock somehow has no price yet.
        current_price = latest.close_price if latest else holding.average_buy_price
        # This is what the shares are worth right now.
        market_value = to_money(current_price * holding.shares_held)
        # This is what the student paid for them.
        cost_basis = to_money(holding.average_buy_price * holding.shares_held)
        # This is the paper profit or loss (not yet realised because they have not sold).
        unrealized_pnl = market_value - cost_basis
        # This adds to the running totals.
        holdings_value += market_value
        # This adds to the running totals.
        holdings_cost += cost_basis
        # This stores the holding in a JSON-friendly shape; money is sent as text to keep exact cents.
        positions.append(
            {
                "ticker": holding.stock.ticker,
                "company_name": holding.stock.company_name,
                "shares_held": holding.shares_held,
                "average_buy_price": str(holding.average_buy_price),
                "current_price": str(current_price),
                "cost_basis": str(cost_basis),
                "market_value": str(market_value),
                "unrealized_pnl": str(unrealized_pnl),
                # This avoids dividing by zero for a free holding, which cannot normally happen.
                "unrealized_pnl_percent": str(to_money(unrealized_pnl / cost_basis * 100)) if cost_basis else "0.00",
                "price_updated_at": latest.recorded_at.isoformat() if latest else None,
            }
        )
    # This reads the KES 100,000 starting balance from the app config.
    starting_balance = to_money(current_app.config["STARTING_VIRTUAL_BALANCE"])
    # Total account value = cash + current value of all shares.
    total_value = to_money(user.virtual_balance + holdings_value)
    # Overall return = how much the account has grown or shrunk since the start.
    total_return = total_value - starting_balance
    # This returns the whole summary.
    return {
        "cash_balance": str(user.virtual_balance),
        "holdings_value": str(to_money(holdings_value)),
        "holdings_cost": str(to_money(holdings_cost)),
        "total_value": str(total_value),
        "starting_balance": str(starting_balance),
        "total_return": str(total_return),
        "total_return_percent": str(to_money(total_return / starting_balance * 100)),
        "positions": positions,
    }
