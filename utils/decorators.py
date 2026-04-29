import jwt
import os
from flask import request, g
from functools import wraps
from db.models import User, UserRole
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('SECRET_KEY')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Token is missing!'}, 401

        if not token:
            return {'message': 'Token is missing!'}, 401

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                return {'message': 'User not found!'}, 401
        except Exception:
            return {'message': 'Token is invalid or expired!'}, 401

        g.user = current_user
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Must be stacked directly inside @token_required so g.user is already set."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.user
        if not user.role_id:
            return {'message': 'Admin access required'}, 403
        role = UserRole.query.filter_by(id=user.role_id, deleted_at=None).first()
        if not role or role.name.upper() != 'ADMIN':
            return {'message': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated


def generateToken(user):
    if not user:
        print("No users found. Run: flask db-seed")
        return
    token = jwt.encode(
        {'user_id': str(user.id), 'exp': datetime.utcnow() + timedelta(hours=24)},
        SECRET_KEY,
        algorithm="HS256",
    )
    return token
