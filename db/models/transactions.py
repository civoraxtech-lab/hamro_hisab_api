from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

# Transaction Table
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('categories.id'))
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'))
    type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('transaction_types.id'))
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey('profiles.id'))
    status = db.Column(db.String(20), default='approved')

    category = db.relationship('Category', backref='transactions')
    group = db.relationship('Group', backref='transactions')
    transaction_type = db.relationship('TransactionType', backref='transactions')
    liabilities = db.relationship('Liability', backref='transaction')

