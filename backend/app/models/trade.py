# This imports datetime so we can store trade execution time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the trades table structure.
class Trade(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "trades"
    # This creates the primary key for each trade.
    id = db.Column(db.Integer, primary_key=True)
    # This links the trade to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links the trade to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This optionally links the trade to an originating order.
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    # This stores trade type such as BUY or SELL.
    trade_type = db.Column(db.String(10), nullable=False)
    # This stores number of shares executed.
    quantity = db.Column(db.Integer, nullable=False)
    # This stores execution price per share.
    price_at_trade = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores total trade value.
    total_value = db.Column(db.Numeric(14, 2), nullable=False)
    # This stores realized profit or loss when applicable.
    realized_pnl = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores when the trade was executed.
    traded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)