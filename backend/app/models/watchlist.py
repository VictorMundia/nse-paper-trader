# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the watchlists table structure.
class Watchlist(db.Model):
    # This sets the exact database table name.
    __tablename__ = "watchlists"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this watchlist to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This stores the watchlist name.
    watchlist_name = db.Column(db.String(100), nullable=False)
    # This stores when the watchlist was created.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # This links one watchlist to many item rows and cascades delete.
    items = db.relationship("WatchlistItem", backref="watchlist", lazy=True, cascade="all, delete-orphan")