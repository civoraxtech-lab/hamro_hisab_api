from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Group Table
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255))
    description = db.Column(db.Text)
    require_verification = db.Column(db.Boolean, default=True)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    members = db.relationship('GroupMember', backref='group', lazy=True)
