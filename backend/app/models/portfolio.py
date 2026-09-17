# This imports datetime so we can set default and update timestamps.
from datetime import datetime
# This imports UniqueConstraint for user-stock uniqueness.
from sqlalchemy import UniqueConstraint
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the portfolio table structure.
class Portfolio(db.Model):
    # This sets the exact database table name.
    __tablename__ = "portfolio"
    # This enforces one row per user-stock pair.
    __table_args__ = (UniqueConstraint("user_id", "stock_id", name="uq_portfolio_user_stock"),)
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this row to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links this row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores current shares held.
    shares_held = db.Column(db.Integer, nullable=False, default=0)
    # This stores average buy price.
    average_buy_price = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    # This stores computed current value.
    current_value = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores computed unrealized P and L.
    unrealized_pnl = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores the last update timestamp.
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)