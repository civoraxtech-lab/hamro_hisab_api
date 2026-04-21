from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Subscription Type Table (The "Who Owes What" Core)
class SubscriptionType(db.Model):
    __tablename__ = 'subscription_types'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

