from ..database import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user_roles.id'))
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50))
    image = db.Column(db.String(255))
    # nullable=True — a user registered via phone may not have email yet, and vice-versa
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
