# This imports datetime so we can store order creation time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the orders table structure.
class Order(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "orders"
    # This creates the primary key for each order.
    id = db.Column(db.Integer, primary_key=True)
    # This links the order to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links the order to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores order type such as BUY or SELL.
    order_type = db.Column(db.String(10), nullable=False)
    # This stores number of shares requested.
    quantity = db.Column(db.Integer, nullable=False)
    # This stores the requested order price.
    order_price = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores order status such as PENDING, FILLED, or CANCELLED.
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    # This stores when the order was created.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)