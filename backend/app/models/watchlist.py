# This imports datetime so we can store watchlist creation time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the watchlists table structure.
class Watchlist(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "watchlists"
    # This creates the primary key for each watchlist.
    id = db.Column(db.Integer, primary_key=True)
    # This links the watchlist to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This stores the watchlist name.
    watchlist_name = db.Column(db.String(100), nullable=False)
    # This stores when the watchlist was created.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)