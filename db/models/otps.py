from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class OneTimePassword(db.Model):
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
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)