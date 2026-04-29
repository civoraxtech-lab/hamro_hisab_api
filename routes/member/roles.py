from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.group_role_service import GroupRoleService

roles_ns = Namespace('roles', description='Group role lookup', path='/api/roles')


@roles_ns.route('/')
class RoleList(Resource):
    @roles_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all group roles"""
        return GroupRoleService.get_all(), 200


@roles_ns.route('/<string:role_id>')
class RoleDetail(Resource):
    @roles_ns.doc(security='Bearer')
    @token_required
    def get(self, role_id):
        """Get a group role by ID"""
        item = GroupRoleService.get_by_id(role_id)
        if not item:
            return {'message': 'Role not found'}, 404
        return item.to_dict, 200
