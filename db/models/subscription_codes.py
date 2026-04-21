from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

#  Subscription Code Table 
class SubscriptionCode(db.Model):
    __tablename__ = 'subscription_codes'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(100), nullable=False)
    discount = db.Column(db.Numeric(10, 2))
    is_percent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

