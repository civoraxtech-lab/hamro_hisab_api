import os
from datetime import datetime, timezone
from flask import g, request, current_app
from flask_restx import Namespace, Resource, fields
from flask_bcrypt import generate_password_hash, check_password_hash
from db import db, User
from utils.decorators import token_required

_ALLOWED_IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'webp'}

settings_ns = Namespace(
    'personal_settings',
    description='User account settings',
    path='/api/personal/settings',
)

update_profile_model = settings_ns.model('UpdateProfile', {
    'firstname': fields.String(example='Ram'),
    'lastname': fields.String(example='Thapa'),
    'email': fields.String(example='ram@example.com'),
    'phone': fields.String(example='+977981234567'),
    'code': fields.String(example='MYCODE123'),
})

change_password_model = settings_ns.model('ChangePassword', {
    'current_password': fields.String(required=True, example='oldpass123'),
    'new_password': fields.String(required=True, example='newpass456'),
})


@settings_ns.route('/')
class UserSettings(Resource):
    @settings_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """Get the current user's account details"""
        u = g.user
        return {
            'id': str(u.id),
            'firstname': u.firstname,
            'lastname': u.lastname,
            'email': u.email,
            'phone': u.phone,
            'code': u.code,
            'image': u.image,
        }, 200

    @settings_ns.doc(security='Bearer')
    @settings_ns.expect(update_profile_model)
    @token_required
    def put(self):
        """Update name, email, phone, or unique code"""
        user = g.user
        data = request.json or {}

        for field in ['firstname', 'lastname', 'email', 'phone', 'code']:
            if field in data:
                value = data[field]
                if value is not None and str(value).strip() != '':
                    setattr(user, field, str(value).strip())

        # Uniqueness check for email
        if 'email' in data and data['email']:
            conflict = User.query.filter(
                User.email == data['email'],
                User.id != user.id,
                User.deleted_at == None,
            ).first()
            if conflict:
                return {'message': 'Email is already in use by another account'}, 409

        # Uniqueness check for phone
        if 'phone' in data and data['phone']:
            conflict = User.query.filter(
                User.phone == data['phone'],
                User.id != user.id,
                User.deleted_at == None,
            ).first()
            if conflict:
                return {'message': 'Phone number is already in use by another account'}, 409

        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Profile updated successfully'}, 200


@settings_ns.route('/image')
class UserAvatar(Resource):
    @settings_ns.doc(security='Bearer')
    @token_required
    def post(self):
        """Upload or replace the user's profile picture"""
        if 'image' not in request.files:
            return {'message': 'No image file provided'}, 400
        file = request.files['image']
        if not file or file.filename == '':
            return {'message': 'No file selected'}, 400

        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in _ALLOWED_IMAGE_EXTS:
            return {'message': 'Unsupported file type. Use jpg, png, or webp'}, 400

        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{g.user.id}.{ext}"
        file.save(os.path.join(upload_dir, filename))

        image_url = f"/uploads/avatars/{filename}"
        g.user.image = image_url
        g.user.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return {'image_url': image_url}, 200


@settings_ns.route('/password')
class ChangePassword(Resource):
    @settings_ns.doc(security='Bearer')
    @settings_ns.expect(change_password_model)
    @token_required
    def put(self):
        """Change account password (requires current password)"""
        user = g.user
        data = request.json or {}
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return {'message': 'Both current and new password are required'}, 400

        if not check_password_hash(user.password, current_password):
            return {'message': 'Current password is incorrect'}, 400

        if len(new_password) < 6:
            return {'message': 'New password must be at least 6 characters'}, 400

        user.password = generate_password_hash(new_password).decode('utf-8')
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Password changed successfully'}, 200
