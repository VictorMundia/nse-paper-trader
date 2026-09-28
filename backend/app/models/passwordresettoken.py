# This imports datetime so we can set default timestamps.
from datetime import datetime

# This imports the shared SQLAlchemy object.
from app.extensions import db


# This class defines the password_reset_tokens table: one row per "forgot password" request.
class PasswordResetToken(db.Model):
    # This sets the exact database table name.
    __tablename__ = "password_reset_tokens"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links the token to the user who asked for it.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # Only a SHA-256 hash is stored, so a database leak does not expose working reset links.
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    # This stores when the link stops working.
    expires_at = db.Column(db.DateTime, nullable=False)
    # This stores when the link was used or replaced by a newer one; empty means still usable.
    used_at = db.Column(db.DateTime, nullable=True)
    # This stores when the link was requested, used for the hourly request limit.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
