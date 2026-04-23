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
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('group_roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'profile_id': str(self.profile_id) if self.profile_id else None,
            'group_id': str(self.group_id) if self.group_id else None,
            'role_id': str(self.role_id) if self.role_id else None,
            'created_at': str(self.created_at)
        }


    
    
