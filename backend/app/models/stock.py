# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the stocks table structure.
class Stock(db.Model):
    # This sets the exact database table name.
    __tablename__ = "stocks"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This stores the unique NSE ticker.
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    # This stores the company name.
    company_name = db.Column(db.String(150), nullable=False)
    # This stores the business sector.
    sector = db.Column(db.String(100), nullable=True)
    # This stores the market name.
    market = db.Column(db.String(50), nullable=True)
    # This stores whether this stock is active.
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    # This links one stock to many price rows.
    prices = db.relationship("Price", backref="stock", lazy=True)
    # This links one stock to many order rows.
    orders = db.relationship("Order", backref="stock", lazy=True)
    # This links one stock to many trade rows.
    trades = db.relationship("Trade", backref="stock", lazy=True)
    # This links one stock to many portfolio rows.
    portfolios = db.relationship("Portfolio", backref="stock", lazy=True)
    # This links one stock to many watchlist item rows.
    watchlist_items = db.relationship("WatchlistItem", backref="stock", lazy=True)