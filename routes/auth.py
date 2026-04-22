import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import request
from flask_restx import Namespace, Resource
from db import User
from flask_bcrypt import check_password_hash

load_dotenv()

auth_ns = Namespace('auth', description='Authentication operations', path='/api/auth')
SECRET_KEY = os.getenv('SECRET_KEY')

@auth_ns.route('/login')
class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data.get('email')).first()

        if user and check_password_hash(user.password, data['password']):
            token = jwt.encode({
                'user_id': str(user.id),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY, algorithm="HS256")

            return {'token': token, 'user': {'firstname': user.firstname, 'id': user.id}}

        return {'message': 'Invalid credentials'}, 401
