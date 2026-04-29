from flask import g, request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required
from utils.context import get_active_profile
from services.group_service import GroupService

group_ns = Namespace('groups', description='Group operations', path='/api/groups')

create_group_model = group_ns.model('CreateGroup', {
    'name': fields.String(required=True, example='Trip to Pokhara'),
    'description': fields.String(example='Expense splitting for our trip'),
    'icon': fields.String(example='trip-icon'),
    'require_verification': fields.Boolean(example=True)
})

update_group_model = group_ns.model('UpdateGroup', {
    'name': fields.String(example='Trip to Pokhara'),
    'description': fields.String(example='Expense splitting for our trip'),
    'icon': fields.String(example='trip-icon'),
    'require_verification': fields.Boolean(example=True)
})

add_member_model = group_ns.model('AddGroupMember', {
    'profile_id': fields.String(required=True, example='uuid-here'),
    'role_id': fields.String(required=True, example='uuid-here')
})

invite_member_model = group_ns.model('InviteGroupMember', {
    'user_id': fields.String(required=True, example='uuid-here')
})


@group_ns.route('/')
class GroupList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List groups the active profile belongs to"""
        profile = get_active_profile(g.user.id)
        return GroupService.get_by_profile(profile.id), 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(create_group_model)
    @token_required
    def post(self):
        """Create a new group (creator is added as ADMIN member)"""
        profile = get_active_profile(g.user.id)
        item = GroupService.create(request.json, profile)
        return {'message': 'Group created', 'id': str(item.id)}, 201


@group_ns.route('/<string:group_id>')
class GroupDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        """Get a group by ID"""
        item = GroupService.get_by_id(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
        return item.to_dict, 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(update_group_model)
    @token_required
    def put(self, group_id):
        """Update a group"""
        item = GroupService.update(group_id, request.json)
        if not item:
            return {'message': 'Group not found'}, 404
        return {'message': 'Group updated'}, 200

    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id):
        """Soft-delete a group"""
        item = GroupService.soft_delete(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
        return {'message': 'Group deleted'}, 200


@group_ns.route('/<string:group_id>/members')
class GroupMemberList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        """List members of a group"""
        return GroupService.get_members(group_id), 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(add_member_model)
    @token_required
    def post(self, group_id):
        """Add a member to a group"""
        item, status_code = GroupService.add_member(group_id, request.json)
        if status_code == 409:
            return {'message': 'Member already exists in this group', 'id': str(item.id)}, 409
        return {'message': 'Member added successfully', 'id': str(item.id)}, 201


@group_ns.route('/<string:group_id>/members/<string:member_id>')
class GroupMemberDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id, member_id):
        """Remove a member from a group"""
        item = GroupService.remove_member(group_id, member_id)
        if not item:
            return {'message': 'Member not found'}, 404
        return {'message': 'Member removed'}, 200


@group_ns.route('/<string:group_id>/invite')
class GroupInvite(Resource):
    @group_ns.doc(security='Bearer')
    @group_ns.expect(invite_member_model)
    @token_required
    def post(self, group_id):
        """Invite a user to a group by user_id"""
        user_id = request.json.get('user_id')
        profile = get_active_profile(g.user.id)
        item, status_code = GroupService.invite_user(group_id, user_id, invited_by_profile_id=profile.id)
        if status_code == 404:
            return {'message': 'User not found'}, 404
        if status_code == 409:
            return item if isinstance(item, dict) else {'message': 'Already invited or a member'}, 409
        return {'message': 'Invitation sent'}, 201


@group_ns.route('/<string:group_id>/leave')
class GroupLeave(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def post(self, group_id):
        """Leave a group"""
        profile = get_active_profile(g.user.id)
        item = GroupService.leave_group(group_id, profile.id)
        if not item:
            return {'message': 'You are not a member of this group'}, 404
        return {'message': 'Left group successfully'}, 200


join_group_model = group_ns.model('JoinGroup', {
    'profile_id': fields.String(required=True, example='uuid-here'),
})


@group_ns.route('/<string:group_id>/join')
class GroupJoin(Resource):
    @group_ns.doc(security='Bearer')
    @group_ns.expect(join_group_model)
    @token_required
    def post(self, group_id):
        """Join a group via QR code scan"""
        data = request.json or {}
        profile_id = data.get('profile_id')
        if not profile_id:
            profile = get_active_profile(g.user.id)
            profile_id = str(profile.id)
        result, status = GroupService.join_group_by_qr(group_id, profile_id)
        return result, status


verify_liability_model = group_ns.model('VerifyLiability', {
    'action': fields.String(required=True, example='approve', description='approve or reject'),
    'code': fields.String(example='ABC123', description='offline member unique code (optional for live verification)'),
})


create_group_transaction_model = group_ns.model('CreateGroupTransaction', {
    'title': fields.String(required=True, example='Hotel'),
    'amount': fields.Float(required=True, example=3000.0),
    'description': fields.String(example='3 nights stay'),
    'paid_by_amounts': fields.Raw(example={'uuid-A': 750.0, 'uuid-B': 750.0}),
    'paid_by_profile_id': fields.String(example='uuid-here'),  # kept for backward compat
    'member_profile_ids': fields.List(fields.String, required=True),
    'split_method': fields.String(example='equal'),
    'exact_amounts': fields.Raw(example={'uuid-A': 500.0}),
    'type_id': fields.String(example='uuid-here'),
    'category_id': fields.String(example='uuid-here'),
    'date': fields.String(example='2026-04-29T00:00:00'),
})


@group_ns.route('/<string:group_id>/transactions')
class GroupTransactionList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        """List all transactions for a group"""
        return GroupService.get_transactions(group_id), 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(create_group_transaction_model)
    @token_required
    def post(self, group_id):
        """Create a group expense transaction"""
        profile = get_active_profile(g.user.id)
        result, status = GroupService.create_group_transaction(group_id, request.json, profile)
        return result, status


@group_ns.route('/<string:group_id>/transactions/<string:tx_id>')
class GroupTransactionDetail(Resource):
    @group_ns.doc(security='Bearer')
    @group_ns.expect(create_group_transaction_model)
    @token_required
    def put(self, group_id, tx_id):
        """Update a group transaction"""
        profile = get_active_profile(g.user.id)
        result, status = GroupService.update_group_transaction(group_id, tx_id, request.json, profile)
        return result, status

    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id, tx_id):
        """Delete a group transaction (admin or initiator only)"""
        profile = get_active_profile(g.user.id)
        result, status = GroupService.delete_group_transaction(group_id, tx_id, profile)
        return result, status


@group_ns.route('/<string:group_id>/transactions/<string:tx_id>/liabilities/<string:liability_id>/verify')
class LiabilityVerify(Resource):
    @group_ns.doc(security='Bearer')
    @group_ns.expect(verify_liability_model)
    @token_required
    def post(self, group_id, tx_id, liability_id):
        """Approve or reject a liability (online or via offline member code)"""
        profile = get_active_profile(g.user.id)
        result, status = GroupService.verify_liability(group_id, tx_id, liability_id, request.json, profile)
        return result, status
