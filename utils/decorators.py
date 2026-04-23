import jwt
import os
from flask import request, g
from functools import wraps
from db.models import User
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

def generateToken(user):
    if not user:
        print("No users found. Run: flask db-seed")
        return
    token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")
    
    return token

        