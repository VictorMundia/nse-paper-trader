# This imports datetime so we can store analysis time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the sentiment_analysis table structure.
class SentimentAnalysis(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "sentiment_analysis"
    # This creates the primary key for each sentiment row.
    id = db.Column(db.Integer, primary_key=True)
    # This links this sentiment record to one news item.
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"), nullable=False)
    # This stores sentiment label such as positive, neutral, or negative.
    sentiment = db.Column(db.String(20), nullable=False)
    # This stores model confidence score.
    confidence_score = db.Column(db.Numeric(5, 2), nullable=True)
    # This stores when analysis was performed.
    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)