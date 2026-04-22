import jwt
import os
import random
import uuid
from datetime import datetime, timezone, timedelta
from flask import g, request
from flask_restx import Namespace, Resource, fields
from flask_bcrypt import generate_password_hash
from db import db, User, OneTimePassword
from utils.decorators import token_required

users_ns = Namespace('users', description='User management', path='/api/users')

# --- Swagger request models ---
phone_login_model = users_ns.model('PhoneLogin', {
    'phone_number': fields.String(required=True, description='Phone number (auto-registers if new)', example='+977981234567')
})

verify_otp_model = users_ns.model('VerifyOtp', {
    'phone_number': fields.String(required=True, description='Phone number'),
    'otp': fields.String(required=True, description='6-digit OTP', example='123456')
})

create_user_model = users_ns.model('CreateUser', {
    'firstname': fields.String(required=True, example='Ram'),
    'lastname': fields.String(required=True, example='Thapa'),
    'email': fields.String(required=True, example='ram@example.com'),
    'phone': fields.String(required=True, example='+977981234567'),
    'password': fields.String(required=True, example='password123')
})

update_user_model = users_ns.model('UpdateUser', {
    'firstname': fields.String(example='Ram'),
    'lastname': fields.String(example='Thapa'),
    'email': fields.String(example='ram@example.com'),
    'phone': fields.String(example='+977981234567'),
    'image': fields.String(example='https://example.com/image.jpg')
})


# --- Phone OTP login ---

@users_ns.route('/login/phone')
class PhoneLogin(Resource):
    @users_ns.expect(phone_login_model)
    def post(self):
        """Step 1: Enter phone number — auto-registers if new, then sends OTP"""
        phone = request.json.get('phone_number')

        user = User.query.filter_by(phone=phone).first()

        if not user:
            # Auto-register with temporary placeholder data
            temp_id = str(uuid.uuid4())[:8]
            user = User(
                firstname='User',
                lastname=temp_id,
                email=f'{temp_id}@temp.hamrohisab.local',
                phone=phone,
                password=generate_password_hash(str(uuid.uuid4())).decode('utf-8')
            )
            db.session.add(user)
            db.session.flush()  # get user.id before commit

        # Invalidate any previous unused OTPs for this phone
        OneTimePassword.query.filter_by(
            phone_or_email=phone, purpose='LOGIN', is_used=False
        ).update({'is_used': True})

        code = str(random.randint(100000, 999999))
        otp = OneTimePassword(
            user_id=user.id,
            phone_or_email=phone,
            code=code,
            purpose='LOGIN',
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        db.session.add(otp)
        db.session.commit()

        # TODO: send via SMS in production — returning otp here for dev/testing only
        return {'message': 'OTP sent successfully', 'otp': code}, 200


@users_ns.route('/verify-otp')
class VerifyOtp(Resource):
    @users_ns.expect(verify_otp_model)
    def post(self):
        """Step 2: Verify OTP and receive JWT access token"""
        data = request.json
        phone = data.get('phone_number')
        code = data.get('otp')

        otp = OneTimePassword.query.filter_by(
            phone_or_email=phone,
            code=code,
            purpose='LOGIN',
            is_used=False
        ).first()

        if not otp:
            return {'message': 'Invalid OTP'}, 401

        expires_at = otp.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return {'message': 'OTP has expired'}, 401

        otp.is_used = True
        db.session.commit()

        user = User.query.get(otp.user_id)
        access_token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, os.getenv('SECRET_KEY'), algorithm="HS256")

        return {
            'access_token': access_token,
            'token_type': 'bearer'
        }, 200


# --- Me ---

@users_ns.route('/me')
class Me(Resource):
    @users_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """Get the currently authenticated user"""
        user = g.user
        return {
            'id': str(user.id),
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'phone': user.phone,
            'image': user.image,
            'code': user.code,
            'created_at': str(user.created_at)
        }, 200

    @users_ns.doc(security='Bearer')
    @users_ns.expect(update_user_model)
    @token_required
    def put(self):
        """Update the currently authenticated user"""
        user = g.user
        data = request.json
        for field in ['firstname', 'lastname', 'email', 'phone', 'image']:
            if field in data:
                setattr(user, field, data[field])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Profile updated successfully'}, 200


# --- CRUD ---

@users_ns.route('/')
class UserList(Resource):
    @users_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active users"""
        users = User.query.filter_by(deleted_at=None).all()
        return [{
            'id': str(u.id),
            'firstname': u.firstname,
            'lastname': u.lastname,
            'email': u.email,
            'phone': u.phone,
            'image': u.image,
            'code': u.code
        } for u in users], 200

    @users_ns.expect(create_user_model)
    def post(self):
        """Register a new user"""
        data = request.json

        if User.query.filter_by(email=data.get('email')).first():
            return {'message': 'Email already registered'}, 409
        if User.query.filter_by(phone=data.get('phone')).first():
            return {'message': 'Phone already registered'}, 409

        user = User(
            firstname=data['firstname'],
            lastname=data['lastname'],
            email=data['email'],
            phone=data['phone'],
            password=generate_password_hash(data['password']).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created successfully', 'id': str(user.id)}, 201


@users_ns.route('/<string:user_id>')
class UserDetail(Resource):
    @users_ns.doc(security='Bearer')
    @token_required
    def get(self, user_id):
        """Get a user by ID"""
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return {'message': 'User not found'}, 404
        return {
            'id': str(user.id),
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'phone': user.phone,
            'image': user.image,
            'code': user.code,
            'created_at': str(user.created_at)
        }, 200

    @users_ns.doc(security='Bearer')
    @users_ns.expect(update_user_model)
    @token_required
    def put(self, user_id):
        """Update a user"""
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return {'message': 'User not found'}, 404

        data = request.json
        for field in ['firstname', 'lastname', 'email', 'phone', 'image']:
            if field in data:
                setattr(user, field, data[field])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'User updated successfully'}, 200

    @users_ns.doc(security='Bearer')
    @token_required
    def delete(self, user_id):
        """Soft delete a user"""
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return {'message': 'User not found'}, 404

        user.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200
