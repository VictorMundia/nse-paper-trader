# This imports datetime so we can store when stock was added.
from datetime import datetime
# This imports the shared SQLAlchemy database object (it re-exports UniqueConstraint).
from app.extensions import db

# This class defines the watchlist_items table structure.
class WatchlistItem(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "watchlist_items"
    # This enforces one stock per watchlist item entry.
    __table_args__ = (db.UniqueConstraint("watchlist_id", "stock_id", name="uq_watchlist_stock"),)
    # This creates the primary key for each watchlist item.
    id = db.Column(db.Integer, primary_key=True)
    # This links the row to a watchlist.
    watchlist_id = db.Column(db.Integer, db.ForeignKey("watchlists.id"), nullable=False)
    # This links the row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores when the stock was added to the watchlist.
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)