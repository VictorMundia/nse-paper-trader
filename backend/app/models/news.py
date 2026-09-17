# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the news table structure.
class News(db.Model):
    # This sets the exact database table name.
    __tablename__ = "news"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This stores article title.
    title = db.Column(db.String(500), nullable=False)
    # This stores article source.
    source = db.Column(db.String(150), nullable=True)
    # This stores article URL.
    article_url = db.Column(db.Text, nullable=True)
    # This stores article content.
    content = db.Column(db.Text, nullable=True)
    # This stores article publication time.
    published_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    # This links one news row to many sentiment rows.
    sentiment_rows = db.relationship("SentimentAnalysis", backref="news", lazy=True, cascade="all, delete-orphan")