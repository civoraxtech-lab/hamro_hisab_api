from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.group_service import GroupService

admin_groups_ns = Namespace(
    'admin-groups',
    description='Admin: full group management',
    path='/api/admin/groups',
)

_update = admin_groups_ns.model('AdminUpdateGroup', {
    'name': fields.String(example='Trip to Pokhara'),
    'description': fields.String(example='Group expense splitting'),
    'icon': fields.String(example='trip-icon'),
    'require_verification': fields.Boolean(example=True),
})


@admin_groups_ns.route('/')
class AdminGroupList(Resource):
    @admin_groups_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all groups"""
        return GroupService.get_all(), 200


@admin_groups_ns.route('/<string:group_id>')
class AdminGroupDetail(Resource):
    @admin_groups_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, group_id):
        """Get any group by ID"""
        item = GroupService.get_by_id(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
        return item.to_dict, 200

    @admin_groups_ns.doc(security='Bearer')
    @admin_groups_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, group_id):
        """Update any group"""
        item = GroupService.update(group_id, request.json)
        if not item:
            return {'message': 'Group not found'}, 404
        return {'message': 'Group updated'}, 200

    @admin_groups_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, group_id):
        """Soft-delete a group"""
        item = GroupService.soft_delete(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
        return {'message': 'Group deleted'}, 200


@admin_groups_ns.route('/<string:group_id>/members')
class AdminGroupMembers(Resource):
    @admin_groups_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, group_id):
        """List all members of any group"""
        return GroupService.get_members(group_id), 200
