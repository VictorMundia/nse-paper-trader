# This imports datetime so we can set default and update timestamps.
from datetime import datetime
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the user_profiles table structure.
class UserProfile(db.Model):
    # This sets the exact database table name.
    __tablename__ = "user_profiles"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this profile to one unique user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    # This stores phone number.
    phone = db.Column(db.String(20), nullable=True)
    # This stores university name.
    university = db.Column(db.String(150), nullable=True)
    # This stores profile picture path or URL.
    profile_picture = db.Column(db.String(255), nullable=True)
    # This stores the last profile update time.
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)