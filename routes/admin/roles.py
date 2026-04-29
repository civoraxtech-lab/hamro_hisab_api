from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.group_role_service import GroupRoleService

admin_roles_ns = Namespace(
    'admin-roles',
    description='Admin: group role management',
    path='/api/admin/roles',
)

_create = admin_roles_ns.model('AdminCreateRole', {
    'name': fields.String(required=True, example='ADMIN'),
    'status': fields.String(example='ACTIVE'),
})

_update = admin_roles_ns.model('AdminUpdateRole', {
    'name': fields.String(example='ADMIN'),
    'status': fields.String(example='ACTIVE'),
})


@admin_roles_ns.route('/')
class AdminRoleList(Resource):
    @admin_roles_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all group roles"""
        return GroupRoleService.get_all(), 200

    @admin_roles_ns.doc(security='Bearer')
    @admin_roles_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a group role"""
        item = GroupRoleService.create(request.json)
        return {'message': 'Group role created', 'id': str(item.id)}, 201


@admin_roles_ns.route('/<string:role_id>')
class AdminRoleDetail(Resource):
    @admin_roles_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, role_id):
        """Get a group role by ID"""
        item = GroupRoleService.get_by_id(role_id)
        if not item:
            return {'message': 'Group role not found'}, 404
        return item.to_dict, 200

    @admin_roles_ns.doc(security='Bearer')
    @admin_roles_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, role_id):
        """Update a group role"""
        item = GroupRoleService.update(role_id, request.json)
        if not item:
            return {'message': 'Group role not found'}, 404
        return {'message': 'Group role updated'}, 200

    @admin_roles_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, role_id):
        """Soft-delete a group role"""
        item = GroupRoleService.soft_delete(role_id)
        if not item:
            return {'message': 'Group role not found'}, 404
        return {'message': 'Group role deleted'}, 200
