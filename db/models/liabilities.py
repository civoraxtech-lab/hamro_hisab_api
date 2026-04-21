from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Liability Table (The "Who Owes What" Core)
class Liability(db.Model):
    __tablename__ = 'liabilities'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = db.Column(UUID(as_uuid=True), db.ForeignKey('transactions.id'))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    settlement_amount = db.Column(db.Numeric(15, 2))
    settled_amount = db.Column(db.Numeric(15, 2), default=0.0)
    initial_payer = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

