# This imports UniqueConstraint for unique user-role pairs.
from sqlalchemy import UniqueConstraint
# This imports the shared SQLAlchemy object.
from app.extensions import db

# This class defines the user_roles junction table structure.
class UserRole(db.Model):
    # This sets the exact database table name.
    __tablename__ = "user_roles"
    # This enforces unique user-role pair rows.
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role_pair"),)
    # This creates the primary key column.
    id = db.Column(db.Integer, primary_key=True)
    # This links this row to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links this row to a role.
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)