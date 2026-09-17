# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the roles table structure.
class Role(db.Model):
    # This sets the exact database table name.
    __tablename__ = "roles"
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This stores unique role name.
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    # This links one role to many user-role assignments.
    user_assignments = db.relationship("UserRole", backref="role", lazy=True)