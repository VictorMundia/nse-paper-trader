# This imports the shared SQLAlchemy database object used by all models.
from app.extensions import db

# This class defines the structure of the stocks table in PostgreSQL.
class Stock(db.Model):
    # This sets the exact table name in the database.
    __tablename__ = "stocks"
    # This creates the primary key column for unique stock IDs.
    id = db.Column(db.Integer, primary_key=True)
    # This stores the stock ticker symbol and requires it to be unique and present.
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    # This stores the company name and requires it to be present.
    company_name = db.Column(db.String(150), nullable=False)
    # This stores the business sector and allows it to be optional.
    sector = db.Column(db.String(100), nullable=True)
    # This stores the market name and allows it to be optional.
    market = db.Column(db.String(50), nullable=True)
    # This stores whether the stock is currently active for trading in the simulator.
    is_active = db.Column(db.Boolean, nullable=False, default=True)