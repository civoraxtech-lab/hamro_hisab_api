from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Subscription Table
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscription_types.id'))
    expiry = db.Column(db.DateTime)
    total_amount = db.Column(db.Numeric(10, 2))
    discount = db.Column(db.Numeric(10, 2))
    is_percent = db.Column(db.Boolean, default=False)
    paid_amount = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

