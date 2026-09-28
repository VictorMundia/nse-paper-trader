# This imports hashlib so we can store a SHA-256 hash of each reset token instead of the token itself.
import hashlib

# This imports secrets, Python's module for generating unguessable random values.
import secrets

# This imports datetime tools for expiry times.
from datetime import datetime, timedelta

# This imports current_app so we can read the frontend address.
from flask import current_app

# This imports the database and the password hasher.
from app.extensions import bcrypt, db

# This imports the reset token model.
from app.models.passwordresettoken import PasswordResetToken

# This imports the User model.
from app.models.user import User

# This imports the background email sender.
from app.services.email_service import send_email_in_background

# This is how long a reset link works.
RESET_TOKEN_LIFETIME = timedelta(minutes=30)

# This caps reset emails per account per hour, so nobody can flood a student's inbox.
MAX_RESET_REQUESTS_PER_HOUR = 3


class ResetTokenError(Exception):
    """The reset link is unknown, already used, or expired."""


def hash_reset_token(raw_token):
    """Return the SHA-256 hash of a reset token as 64 hex characters."""
    # A fast hash is safe here because the token is 256 random bits; bcrypt is only needed for guessable passwords.
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def set_new_password(user, new_password):
    """Hash and save a new password, and mark every older login token as no longer valid."""
    # This stores only the bcrypt hash of the new password.
    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    # Rounded to the second because token issue times (iat) are whole seconds; see extensions.py.
    user.password_changed_at = datetime.utcnow().replace(microsecond=0)


def request_password_reset(email):
    """Email a reset link if the account exists; silently do nothing otherwise."""
    # This looks up the account.
    user = User.query.filter_by(email=email).first()
    # Unknown emails get no email, but the route still gives the same reply, so accounts cannot be discovered.
    if user is None:
        # This ends quietly.
        return
    # This is the start of the rate-limit window.
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    # This counts how many links this account requested in the last hour.
    recent_requests = PasswordResetToken.query.filter(
        # This keeps only this user's tokens.
        PasswordResetToken.user_id == user.id,
        # This keeps only tokens from the last hour.
        PasswordResetToken.created_at >= one_hour_ago,
    ).count()
    # This stops after the hourly limit.
    if recent_requests >= MAX_RESET_REQUESTS_PER_HOUR:
        # This records the blocked request in the server console only.
        print(f"[Password reset] Rate limit reached for user {user.id}; no email sent.")
        # This ends quietly.
        return
    # Only the newest link should work, so any older unused links are retired now.
    PasswordResetToken.query.filter_by(user_id=user.id, used_at=None).update({"used_at": datetime.utcnow()})
    # This creates a 43-character random token that is practically impossible to guess.
    raw_token = secrets.token_urlsafe(32)
    # This stores the hash and expiry; the raw token only ever appears in the email.
    db.session.add(PasswordResetToken(user_id=user.id, token_hash=hash_reset_token(raw_token), expires_at=datetime.utcnow() + RESET_TOKEN_LIFETIME))
    # This saves the token.
    db.session.commit()
    # This builds the link to the frontend reset page.
    reset_link = f"{current_app.config['FRONTEND_URL']}/reset-password?token={raw_token}"
    # This sends the email without delaying the response.
    send_email_in_background(
        # This is the recipient.
        user.email,
        # This is the subject line.
        "Reset your NSE Paper Trader password",
        # This is the email body.
        f"Hello {user.full_name},\n\n"
        f"We received a request to reset your NSE Paper Trader password.\n"
        f"Open this link to choose a new password (it works once and expires in 30 minutes):\n\n"
        f"{reset_link}\n\n"
        f"If you did not ask for this, you can ignore this email; your password will not change.",
    )


def reset_password_with_token(raw_token, new_password):
    """Set a new password using a reset link; raises ResetTokenError if the link is not valid."""
    # This finds the token by its hash and locks it so the same link cannot be used twice at the same moment.
    token = PasswordResetToken.query.filter_by(token_hash=hash_reset_token(raw_token)).with_for_update().first()
    # This rejects unknown, already-used, and expired links with one message, so none can be told apart.
    if token is None or token.used_at is not None or token.expires_at < datetime.utcnow():
        # This undoes nothing but releases the lock.
        db.session.rollback()
        # This tells the route the link is not valid.
        raise ResetTokenError("This reset link is invalid or has expired. Please request a new one.")
    # This saves the new password and logs out every existing session.
    set_new_password(token.user, new_password)
    # This makes the link single-use.
    token.used_at = datetime.utcnow()
    # This saves both changes together.
    db.session.commit()
