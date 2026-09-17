# This imports datetime so we can store update time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the portfolio table structure.
class Portfolio(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "portfolio"
    # This enforces one portfolio row per user-stock pair.
    __table_args__ = (db.UniqueConstraint("user_id", "stock_id", name="uq_portfolio_user_stock"),)
    # This creates the primary key for each portfolio row.
    id = db.Column(db.Integer, primary_key=True)
    # This links the portfolio row to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links the portfolio row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores shares currently held.
    shares_held = db.Column(db.Integer, nullable=False, default=0)
    # This stores average buy price for held shares.
    average_buy_price = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    # This stores current market value of the holding.
    current_value = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores unrealized profit or loss.
    unrealized_pnl = db.Column(db.Numeric(14, 2), nullable=True)
    # This stores when this row was last updated.
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)