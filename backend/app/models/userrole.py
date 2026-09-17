# This imports the shared SQLAlchemy database object.
from app.extensions import db

# This class defines the user_roles junction table structure.
class UserRole(db.Model):
    # This sets the table name in PostgreSQL.
    __tablename__ = "user_roles"
    # This enforces one unique role assignment per user-role pair.
    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="uq_user_role_pair"),)
    # This creates the primary key for each assignment row.
    id = db.Column(db.Integer, primary_key=True)
    # This links the assignment to a user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # This links the assignment to a role.
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)