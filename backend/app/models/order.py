# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the orders table structure.
class Order(db.Model):
    # This sets the exact database table name.
    __tablename__ = "orders"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this order to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links this order to a stock.
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)
    # This stores order type such as BUY or SELL.
    order_type = db.Column(db.String(10), nullable=False)
    # This stores quantity requested.
    quantity = db.Column(db.Integer, nullable=False)
    # This stores order price.
    order_price = db.Column(db.Numeric(12, 2), nullable=False)
    # This stores order status such as PENDING or FILLED.
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    # This stores order creation time.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # This links one order to many trades that came from it.
    trades = db.relationship("Trade", backref="order", lazy=True)