# This imports datetime so we can store publish time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the news table structure.
class News(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "news"
    # This creates the primary key for each news row.
    id = db.Column(db.Integer, primary_key=True)
    # This stores news headline.
    title = db.Column(db.String(500), nullable=False)
    # This stores source name.
    source = db.Column(db.String(150), nullable=True)
    # This stores article URL.
    article_url = db.Column(db.Text, nullable=True)
    # This stores article body text.
    content = db.Column(db.Text, nullable=True)
    # This stores when the article was published.
    published_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)