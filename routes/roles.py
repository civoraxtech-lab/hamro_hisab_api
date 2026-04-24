from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, GroupRole
from utils.decorators import token_required
from controllers.member.group_roles import GroupRoleController

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
        items = GroupRoleController.index()
        return items, 200

    @roles_ns.doc(security='Bearer')
    @roles_ns.expect(create_model)
    @token_required
    def post(self):
        item = GroupRoleController.create(request.json)
        return {'message': 'Group Roles created', 'id': str(item.id)}, 201


@roles_ns.route('/<string:role_id>')
class RoleDetail(Resource):
    @roles_ns.doc(security='Bearer')
    @token_required
    def get(self, role_id):
        item = GroupRoleController.show(role_id)
        if not item:
            return {'message': 'Role not found'}, 404
        return item,200

    @roles_ns.doc(security='Bearer')
    @roles_ns.expect(update_model)
    @token_required
    def put(self, role_id):
        updated_item = GroupRoleController.update(role_id, request.json)
        if not updated_item:
            return {'message': 'Group Role not found'}, 404
        return {'message': 'Group Role updated'}, 200

    @roles_ns.doc(security='Bearer')
    @token_required
    def delete(self, role_id):
        item = GroupRoleController.delete(role_id)
        if not item:
            return {'message': 'Group Role not found'}, 404
            
        return {'message': 'Group Role deleted'}, 200
