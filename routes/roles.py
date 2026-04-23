from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, GroupRole
from utils.decorators import token_required

roles_ns = Namespace('roles', description='Role operations', path='/api/roles')

create_model = roles_ns.model('CreateRole', {
    'name': fields.String(required=True, example='ADMIN'),
    'status': fields.String(example='ACTIVE')
})

update_model = roles_ns.model('UpdateRole', {
    'name': fields.String(example='ADMIN'),
    'status': fields.String(example='ACTIVE')
})

@roles_ns.route('/')
class RoleList(Resource):
    @roles_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all roles"""
        items = GroupRole.query.filter_by(deleted_at=None).all()
        return [serialize(r) for r in items], 200

    @roles_ns.doc(security='Bearer')
    @roles_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a role"""
        data = request.json
        item = GroupRole(name=data['name'], status=data.get('status', 'ACTIVE'))
        db.session.add(item)
        db.session.commit()
        return {'message': 'Role created', 'id': str(item.id)}, 201


@roles_ns.route('/<string:role_id>')
class RoleDetail(Resource):
    @roles_ns.doc(security='Bearer')
    @token_required
    def get(self, role_id):
        """Get a role by ID"""
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return {'message': 'Role not found'}, 404
        return serialize(item), 200

    @roles_ns.doc(security='Bearer')
    @roles_ns.expect(update_model)
    @token_required
    def put(self, role_id):
        """Update a role"""
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return {'message': 'Role not found'}, 404
        data = request.json
        for field in ['name', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Role updated'}, 200

    @roles_ns.doc(security='Bearer')
    @token_required
    def delete(self, role_id):
        """Delete a role"""
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return {'message': 'Role not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Role deleted'}, 200
