# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports UniqueConstraint for watchlist-stock uniqueness.
from sqlalchemy import UniqueConstraint
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the watchlist_items table structure.
class WatchlistItem(db.Model):
    # This sets the exact database table name.
    __tablename__ = "watchlist_items"
    # This enforces one stock entry per watchlist.
    __table_args__ = (UniqueConstraint("watchlist_id", "stock_id", name="uq_watchlist_stock"),)
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this row to a watchlist.
    watchlist_id = db.Column(db.Integer, db.ForeignKey("watchlists.id"), nullable=False)
    # This links this row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores when this stock was added.
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)