from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Profile
from utils.decorators import token_required

profiles_ns = Namespace('profiles', description='Profile operations', path='/api/profiles')

create_model = profiles_ns.model('CreateProfile', {
    'name': fields.String(required=True, example='Home'),
    'is_default': fields.Boolean(example=False)
})

update_model = profiles_ns.model('UpdateProfile', {
    'name': fields.String(example='Home'),
    'is_default': fields.Boolean(example=False)
})


def serialize(p):
    return {
        'id': str(p.id),
        'user_id': str(p.user_id),
        'name': p.name,
        'is_default': p.is_default,
        'created_at': str(p.created_at)
    }


@profiles_ns.route('/')
class ProfileList(Resource):
    @profiles_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List current user's profiles"""
        items = Profile.query.filter_by(user_id=g.user.id, deleted_at=None).all()
        return [serialize(p) for p in items], 200

    @profiles_ns.doc(security='Bearer')
    @profiles_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a profile"""
        data = request.json
        item = Profile(
            user_id=g.user.id,
            name=data['name'],
            is_default=data.get('is_default', False)
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Profile created', 'id': str(item.id)}, 201


@profiles_ns.route('/<string:profile_id>')
class ProfileDetail(Resource):
    @profiles_ns.doc(security='Bearer')
    @token_required
    def get(self, profile_id):
        """Get a profile by ID"""
        item = Profile.query.filter_by(id=profile_id, deleted_at=None).first()
        if not item:
            return {'message': 'Profile not found'}, 404
        return serialize(item), 200

    @profiles_ns.doc(security='Bearer')
    @profiles_ns.expect(update_model)
    @token_required
    def put(self, profile_id):
        """Update a profile"""
        item = Profile.query.filter_by(id=profile_id, deleted_at=None).first()
        if not item:
            return {'message': 'Profile not found'}, 404
        data = request.json
        for field in ['name', 'is_default']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Profile updated'}, 200

    @profiles_ns.doc(security='Bearer')
    @token_required
    def delete(self, profile_id):
        """Delete a profile"""
        item = Profile.query.filter_by(id=profile_id, deleted_at=None).first()
        if not item:
            return {'message': 'Profile not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Profile deleted'}, 200
