import os
import random
import string
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import request
from flask_restx import Namespace, Resource
from db import User
from db.models.otps import OneTimePassword
from db.database import db
from flask_bcrypt import check_password_hash, generate_password_hash
from utils.decorators import generateToken

load_dotenv()

auth_ns = Namespace('auth', description='Authentication operations', path='/api/auth')
SECRET_KEY = os.getenv('SECRET_KEY')
_VERIFIED_TOKEN_TTL = 15  # minutes


def _find_user(identifier):
    return (
        User.query.filter_by(email=identifier).first() or
        User.query.filter_by(phone=identifier).first()
    )


def _user_data(user):
    return {
        'id': str(user.id),
        'firstname': user.firstname,
        'lastname': user.lastname,
        'email': user.email,
        'phone': user.phone,
        'image': user.image,
    }


def _make_verified_token(phone_or_email, purpose):
    """Short-lived JWT that proves OTP was verified — unlocks setup or reset-password."""
    return jwt.encode(
        {
            'phone_or_email': phone_or_email,
            'purpose': purpose,
            'exp': datetime.utcnow() + timedelta(minutes=_VERIFIED_TOKEN_TTL),
        },
        SECRET_KEY,
        algorithm='HS256',
    )


def _decode_verified_token(token, expected_purpose):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if data.get('purpose') != expected_purpose:
            return None, 'Invalid token purpose'
        return data, None
    except jwt.ExpiredSignatureError:
        return None, 'Verification expired — please request a new OTP'
    except Exception:
        return None, 'Invalid verification token'


def _is_phone(identifier):
    """True when identifier looks like a phone number (digits / + / spaces / dashes)."""
    cleaned = identifier.replace('+', '').replace('-', '').replace(' ', '')
    return cleaned.isdigit() and len(cleaned) >= 7


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_ns.route('/login')
class Login(Resource):
    def post(self):
        data = request.json or {}
        identifier = (data.get('email') or data.get('phone') or '').strip()
        if not identifier:
            return {'message': 'Email or phone is required'}, 400

        user = _find_user(identifier)
        if user and check_password_hash(user.password, data.get('password', '')):
            return {'token': generateToken(user), 'user': _user_data(user)}

        return {'message': 'Invalid credentials'}, 401


# ─── OTP ──────────────────────────────────────────────────────────────────────

@auth_ns.route('/request-otp')
class RequestOTP(Resource):
    def post(self):
        data = request.json or {}
        identifier = (data.get('phone_or_email') or '').strip()
        purpose = (data.get('purpose') or '').strip().upper()

        if not identifier:
            return {'message': 'phone_or_email is required'}, 400
        if purpose not in ('REGISTRATION', 'PASSWORD_RESET'):
            return {'message': 'purpose must be REGISTRATION or PASSWORD_RESET'}, 400

        user = _find_user(identifier)

        if purpose == 'REGISTRATION' and user:
            return {'message': 'An account already exists with this email or phone'}, 409
        if purpose == 'PASSWORD_RESET' and not user:
            return {'message': 'No account found with that email or phone'}, 404

        code = ''.join(random.choices(string.digits, k=6))
        otp = OneTimePassword(
            user_id=user.id if user else None,
            phone_or_email=identifier,
            code=code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.session.add(otp)
        db.session.commit()

        # TODO: send via SMS / email provider
        # Remove 'code' from the response before going to production
        return {'message': 'OTP sent successfully', 'code': code}, 200


@auth_ns.route('/verify-otp')
class VerifyOTP(Resource):
    def post(self):
        data = request.json or {}
        identifier = (data.get('phone_or_email') or '').strip()
        code = (data.get('code') or '').strip()
        purpose = (data.get('purpose') or '').strip().upper()

        if not all([identifier, code, purpose]):
            return {'message': 'phone_or_email, code, and purpose are required'}, 400

        otp = (
            OneTimePassword.query
            .filter_by(phone_or_email=identifier, code=code, purpose=purpose, is_used=False)
            .filter(OneTimePassword.expires_at > datetime.utcnow())
            .order_by(OneTimePassword.created_at.desc())
            .first()
        )

        if not otp:
            return {'message': 'Invalid or expired OTP'}, 401

        otp.is_used = True
        db.session.commit()

        return {'verified_token': _make_verified_token(identifier, purpose)}, 200


# ─── Registration Setup ───────────────────────────────────────────────────────

@auth_ns.route('/complete-setup')
class CompleteSetup(Resource):
    def post(self):
        data = request.json or {}
        verified_token = (data.get('verified_token') or '').strip()

        token_data, error = _decode_verified_token(verified_token, 'REGISTRATION')
        if error:
            return {'message': error}, 401

        identifier = token_data['phone_or_email']
        if _find_user(identifier):
            return {'message': 'Account already exists'}, 409

        firstname = (data.get('firstname') or '').strip()
        lastname = (data.get('lastname') or '').strip()
        password = (data.get('password') or '').strip()

        if not all([firstname, lastname, password]):
            return {'message': 'firstname, lastname, and password are required'}, 400

        if _is_phone(identifier):
            phone = identifier
            email = (data.get('email') or '').strip() or None
        else:
            email = identifier
            phone = (data.get('phone') or '').strip() or None

        hashed = generate_password_hash(password).decode('utf-8')
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone=phone,
            password=hashed,
        )
        db.session.add(user)
        db.session.commit()

        return {'token': generateToken(user), 'user': _user_data(user)}, 201


# ─── Forgot Password ──────────────────────────────────────────────────────────

@auth_ns.route('/reset-password')
class ResetPassword(Resource):
    def post(self):
        data = request.json or {}
        verified_token = (data.get('verified_token') or '').strip()

        token_data, error = _decode_verified_token(verified_token, 'PASSWORD_RESET')
        if error:
            return {'message': error}, 401

        identifier = token_data['phone_or_email']
        user = _find_user(identifier)
        if not user:
            return {'message': 'User not found'}, 404

        password = (data.get('password') or '').strip()
        if not password:
            return {'message': 'password is required'}, 400

        user.password = generate_password_hash(password).decode('utf-8')
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return {'token': generateToken(user), 'user': _user_data(user)}
