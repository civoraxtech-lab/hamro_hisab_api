import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import request
from flask_restx import Namespace, Resource
from db import User
from flask_bcrypt import check_password_hash
from utils.decorators import generateToken

load_dotenv()

auth_ns = Namespace('auth', description='Authentication operations', path='/api/auth')
SECRET_KEY = os.getenv('SECRET_KEY')

@auth_ns.route('/login')
class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data.get('email')).first()

        if user and check_password_hash(user.password, data['password']):
            token = generateToken(user)

            return {'token': token, 'user': {'firstname': user.firstname, 'id': user.id}}

        return {'message': 'Invalid credentials'}, 401
