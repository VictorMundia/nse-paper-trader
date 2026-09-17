# This imports datetime so we can store capture time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the prices table structure.
class Price(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "prices"
    # This creates the primary key for each price row.
    id = db.Column(db.Integer, primary_key=True)
    # This links the price row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores the opening price.
    open_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the highest price.
    high_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the lowest price.
    low_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the close or latest captured price.
    close_price = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores traded volume.
    volume = db.Column(db.BigInteger, nullable=True)
    # This stores when this price was recorded.
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)