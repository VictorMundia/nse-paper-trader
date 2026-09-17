# This imports datetime so we can store profile update time.
from datetime import datetime
# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the user_profiles table structure.
class UserProfile(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "user_profiles"
    # This creates the primary key for each profile row.
    id = db.Column(db.Integer, primary_key=True)
    # This links the profile to one user and enforces one profile per user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    # This stores the user phone number.
    phone = db.Column(db.String(20), nullable=True)
    # This stores university name.
    university = db.Column(db.String(150), nullable=True)
    # This stores optional profile picture URL or path.
    profile_picture = db.Column(db.String(255), nullable=True)
    # This stores when the profile was last updated.
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)