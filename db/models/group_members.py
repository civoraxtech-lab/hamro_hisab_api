from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Group Member Table
class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profiles.id'))
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    
    
