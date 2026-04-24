from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Liability Table (The "Who Owes What" Core)
class Liability(db.Model):
    __tablename__ = 'liabilities'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = db.Column(UUID(as_uuid=True), db.ForeignKey('transactions.id'), index=True)
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profiles.id'), index=True)
    settlement_amount = db.Column(db.Numeric(15, 2))
    settled_amount = db.Column(db.Numeric(15, 2), default=0.0)
    initial_payer = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    profile = db.relationship('Profile', backref='liabalities')
   
    @property
    def to_dict(self):
        return {
            'id': str(self.id),
            'transaction_id': str(self.transaction_id) if self.transaction_id else None,
            'profile_id': str(self.profile_id) if self.profile_id else None,
            'settlement_amount': float(self.settlement_amount) if self.settlement_amount else None,
            'settled_amount': float(self.settled_amount) if self.settled_amount else 0.0,
            'initial_payer': self.initial_payer,
            'is_verified': self.is_verified,
            'created_at': str(self.created_at)
        }