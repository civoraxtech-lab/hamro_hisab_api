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

users_ns = Namespace('users', description='User auth and profile', path='/api/users')

phone_login_model = users_ns.model('PhoneLogin', {
    'phone_number': fields.String(required=True, example='+977981234567')
})

verify_otp_model = users_ns.model('VerifyOtp', {
    'phone_number': fields.String(required=True),
    'otp': fields.String(required=True, example='123456')
})

update_user_model = users_ns.model('UpdateUser', {
    'firstname': fields.String(example='Ram'),
    'lastname': fields.String(example='Thapa'),
    'email': fields.String(example='ram@example.com'),
    'phone': fields.String(example='+977981234567'),
    'image': fields.String(example='https://example.com/image.jpg')
})


@users_ns.route('/login/phone')
class PhoneLogin(Resource):
    @users_ns.expect(phone_login_model)
    def post(self):
        """Step 1: Enter phone — auto-registers if new, sends OTP"""
        phone = request.json.get('phone_number')
        user = User.query.filter_by(phone=phone).first()
        if not user:
            temp_id = str(uuid.uuid4())[:8]
            user = User(
                firstname='User',
                lastname=temp_id,
                email=f'{temp_id}@temp.hamrohisab.local',
                phone=phone,
                password=generate_password_hash(str(uuid.uuid4())).decode('utf-8')
            )
            db.session.add(user)
            db.session.flush()

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
        return {'message': 'OTP sent successfully', 'otp': code}, 200


@users_ns.route('/verify-otp')
class VerifyOtp(Resource):
    @users_ns.expect(verify_otp_model)
    def post(self):
        """Step 2: Verify OTP and receive JWT"""
        data = request.json
        phone = data.get('phone_number')
        code = data.get('otp')

        otp = OneTimePassword.query.filter_by(
            phone_or_email=phone, code=code, purpose='LOGIN', is_used=False
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
        access_token = jwt.encode(
            {'user_id': str(user.id), 'exp': datetime.now(timezone.utc) + timedelta(hours=24)},
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )
        return {'access_token': access_token, 'token_type': 'bearer'}, 200


@users_ns.route('/search')
class UserSearch(Resource):
    @users_ns.doc(security='Bearer', params={'q': 'Search by name, email, phone or code (min 2 chars)'})
    @token_required
    def get(self):
        """Search users by name, email, phone or code"""
        from db.models import Profile
        q = request.args.get('q', '').strip()
        if len(q) < 2:
            return [], 200
        current_user_id = g.user.id
        users = User.query.filter(
            db.or_(
                User.firstname.ilike(f'%{q}%'),
                User.lastname.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.phone.ilike(f'%{q}%'),
                User.code.ilike(f'%{q}%'),
            ),
            User.deleted_at == None,
            User.id != current_user_id,
        ).limit(20).all()

        result = []
        for u in users:
            profile = Profile.query.filter_by(user_id=u.id, is_default=True, deleted_at=None).first()
            if not profile:
                profile = Profile.query.filter_by(user_id=u.id, deleted_at=None).first()
            result.append({
                'id': str(u.id),
                'firstname': u.firstname,
                'lastname': u.lastname,
                'email': u.email,
                'phone': u.phone,
                'image': u.image,
                'code': u.code,
                'profile_id': str(profile.id) if profile else None,
            })
        return result, 200


@users_ns.route('/me')
class Me(Resource):
    @users_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """Get the currently authenticated user"""
        u = g.user
        return {
            'id': str(u.id),
            'firstname': u.firstname,
            'lastname': u.lastname,
            'email': u.email,
            'phone': u.phone,
            'image': u.image,
            'code': u.code,
            'created_at': str(u.created_at)
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
