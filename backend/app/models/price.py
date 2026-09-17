# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the prices table structure.
class Price(db.Model):
    # This sets the exact database table name.
    __tablename__ = "prices"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this price row to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores the open price.
    open_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the high price.
    high_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the low price.
    low_price = db.Column(db.Numeric(12, 2), nullable=True)
    # This stores the close price.
    close_price = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores traded volume.
    volume = db.Column(db.BigInteger, nullable=True)
    # This stores when this row was recorded.
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)