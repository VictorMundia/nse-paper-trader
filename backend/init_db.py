# This imports the app factory so we can build a configured Flask application.
from app import create_app
# This imports text so we can run a raw SQL statement.
from sqlalchemy import text
# This imports the shared SQLAlchemy object so we can create database tables.
from app.extensions import db
# This imports all model classes so SQLAlchemy knows every table definition.
import app.models

# This creates a configured Flask app instance.
app = create_app()

# This checks if this file is executed directly from the terminal.
if __name__ == "__main__":
    # This opens the Flask application context required for database operations.
    with app.app_context():
        # This creates all tables that do not already exist in PostgreSQL.
        db.create_all()
        # create_all never adds columns to existing tables, so columns added later are added here; IF NOT EXISTS makes it safe to re-run.
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP NULL"))
        # This saves the column change.
        db.session.commit()
        # This prints a success message after table creation completes.
        print("Database tables created successfully.")