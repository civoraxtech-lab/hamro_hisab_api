from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.user_service import UserService

admin_users_ns = Namespace(
    'admin-users',
    description='Admin: user management',
    path='/api/admin/users',
)

_update = admin_users_ns.model('AdminUpdateUser', {
    'firstname': fields.String(example='Ram'),
    'lastname': fields.String(example='Thapa'),
    'email': fields.String(example='ram@example.com'),
    'phone': fields.String(example='+977981234567'),
    'image': fields.String(example='https://example.com/image.jpg'),
})


@admin_users_ns.route('/')
class AdminUserList(Resource):
    @admin_users_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all active users"""
        return UserService.get_all(), 200


@admin_users_ns.route('/<string:user_id>')
class AdminUserDetail(Resource):
    @admin_users_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, user_id):
        """Get any user by ID"""
        user = UserService.get_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return UserService.serialize(user), 200

    @admin_users_ns.doc(security='Bearer')
    @admin_users_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, user_id):
        """Update any user"""
        user = UserService.update(user_id, request.json)
        if not user:
            return {'message': 'User not found'}, 404
        return {'message': 'User updated'}, 200

    @admin_users_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, user_id):
        """Soft-delete a user"""
        user = UserService.soft_delete(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return {'message': 'User deleted'}, 200
