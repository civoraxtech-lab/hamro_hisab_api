from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


# Profile Table
class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    
    user = db.relationship('User', backref='profiles')
