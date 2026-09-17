# This imports datetime so we can set default timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the sentiment_analysis table structure.
class SentimentAnalysis(db.Model):
    # This sets the exact database table name.
    __tablename__ = "sentiment_analysis"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this sentiment row to one news row.
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"), nullable=False)
    # This stores sentiment label.
    sentiment = db.Column(db.String(20), nullable=False)
    # This stores model confidence score.
    confidence_score = db.Column(db.Numeric(5, 2), nullable=True)
    # This stores sentiment analysis timestamp.
    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)