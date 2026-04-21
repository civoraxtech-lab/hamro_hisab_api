import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

db = SQLAlchemy()

# 1. User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50))
    image = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 2. Group Table
class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255))
    description = db.Column(db.Text)
    require_verification = db.Column(db.Boolean, default=True)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 3. Category Table
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(255))
    iconColor = db.Column(db.String(50))
    is_default = db.Column(db.Boolean, default=False)
    created_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 4. Roles Table
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 5. Group Member Table
class GroupMember(db.Model):
    __tablename__ = 'group_members'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    group_id = db.Column(UUID(as_uuid=True), db.ForeignKey('groups.id'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 6. Transaction Type Table
class TransactionType(db.Model):
    __tablename__ = 'transaction_types'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 7. Transaction Table
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


# 8. Liability Table (The "Who Owes What" Core)
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

# 9. Subscription Type Table (The "Who Owes What" Core)
class SubscriptionType(db.Model):
    __tablename__ = 'subscription_types'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

# 10. Subscription Table
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

# 11. Subscription Code Table 
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

class Otp(db.Model):
    __tablename__ = 'otps'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Link to the user, but keep it nullable if you verify BEFORE registration
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    phone_or_email = db.Column(db.String(150), nullable=False)
    # The actual code (usually 4 or 6 digits)
    code = db.Column(db.String(6), nullable=False)
    # Purpose of the OTP (e.g., 'REGISTRATION', 'PASSWORD_RESET', 'SETTLEMENT')
    purpose = db.Column(db.String(50))
    # Security columns
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)