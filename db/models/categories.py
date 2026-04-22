from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


# Category Table
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255))
    iconColor = db.Column(db.String(50))
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    