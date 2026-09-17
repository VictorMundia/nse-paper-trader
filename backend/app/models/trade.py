# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the trades table structure.
class Trade(db.Model):
    # This sets the exact database table name.
    __tablename__ = "trades"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this trade to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links this trade to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This links this trade to an order if it came from one.
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    # This stores trade type such as BUY or SELL.
    trade_type = db.Column(db.String(10), nullable=False)
    # This stores executed quantity.
    quantity = db.Column(db.Integer, nullable=False)
    # This stores executed unit price.
    price_at_trade = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores total trade value.
    total_value = db.Column(db.Numeric(14, 2), nullable=False)
    # This stores realized profit or loss when applicable.
    realized_pnl = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores execution timestamp.
    traded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)