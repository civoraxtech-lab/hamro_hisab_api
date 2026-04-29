from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class GroupInvitation(db.Model):
    __tablename__ = 'group_invitations'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'), nullable=False, index=True)
    invited_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    invited_by_profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profiles.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending / accepted / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'group_id': str(self.group_id),
            'invited_user_id': str(self.invited_user_id),
            'invited_by_profile_id': str(self.invited_by_profile_id) if self.invited_by_profile_id else None,
            'status': self.status,
            'created_at': str(self.created_at),
        }
