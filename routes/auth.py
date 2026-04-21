import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from db import User, db
from flask_bcrypt import check_password_hash # Recommended for real passwords

# Load the .env file
load_dotenv()

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.getenv('SECRET_KEY')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password, data['password']): 
        token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({'token': token, 'user': {'firstname': user.firstname, 'id': user.id}})
    
    return jsonify({'message': 'Invalid credentials'}), 401