# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the roles table structure.
class Role(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "roles"
    # This creates the primary key for each role.
    id = db.Column(db.Integer, primary_key=True)
    # This stores role name such as STUDENT or ADMIN and enforces uniqueness.
    role_name = db.Column(db.String(50), unique=True, nullable=False)