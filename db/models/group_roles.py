from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# GroupRoles Table
class GroupRole(db.Model):
    __tablename__ = 'group_roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'status': self.status,
            'created_at': str(self.created_at)
        }