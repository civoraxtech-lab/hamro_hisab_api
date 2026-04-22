from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Group, GroupMember
from utils.decorators import token_required

group_ns = Namespace('groups', description='Group operations', path='/api/groups')

create_group_model = group_ns.model('CreateGroup', {
    'name': fields.String(required=True, example='Trip to Pokhara'),
    'description': fields.String(example='Expense splitting for our trip'),
    'icon': fields.String(example='trip-icon'),
    'require_verification': fields.Boolean(example=True),
    'profile_id': fields.String(required=True, example='uuid-here')
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


def serialize_group(g_obj):
    return {
        'id': str(g_obj.id),
        'name': g_obj.name,
        'description': g_obj.description,
        'icon': g_obj.icon,
        'require_verification': g_obj.require_verification,
        'created_by': str(g_obj.created_by) if g_obj.created_by else None,
        'created_at': str(g_obj.created_at)
    }


def serialize_member(m):
    return {
        'id': str(m.id),
        'profile_id': str(m.profile_id) if m.profile_id else None,
        'group_id': str(m.group_id) if m.group_id else None,
        'role_id': str(m.role_id) if m.role_id else None,
        'created_at': str(m.created_at)
    }


# --- Group CRUD ---

@group_ns.route('/')
class GroupList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all groups"""
        items = Group.query.filter_by(deleted_at=None).all()
        return [serialize_group(g) for g in items], 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(create_group_model)
    @token_required
    def post(self):
        """Create a group"""
        data = request.json
        item = Group(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            require_verification=data.get('require_verification', True),
            created_by=data['profile_id']
        )
        db.session.add(item)
        db.session.flush()

        # Auto-add creator as a member
        member = GroupMember(
            profile_id=data['profile_id'],
            group_id=item.id
        )
        db.session.add(member)
        db.session.commit()
        return {'message': 'Group created', 'id': str(item.id)}, 201


@group_ns.route('/<string:group_id>')
class GroupDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        """Get a group by ID"""
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return {'message': 'Group not found'}, 404
        return serialize_group(item), 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(update_group_model)
    @token_required
    def put(self, group_id):
        """Update a group"""
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return {'message': 'Group not found'}, 404
        data = request.json
        for field in ['name', 'description', 'icon', 'require_verification']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Group updated'}, 200

    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id):
        """Delete a group"""
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return {'message': 'Group not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Group deleted'}, 200


# --- Group Members ---

@group_ns.route('/<string:group_id>/members')
class GroupMemberList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        """List members of a group"""
        members = GroupMember.query.filter_by(group_id=group_id, deleted_at=None).all()
        return [serialize_member(m) for m in members], 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(add_member_model)
    @token_required
    def post(self, group_id):
        """Add a member to a group"""
        data = request.json
        existing = GroupMember.query.filter_by(
            group_id=group_id, profile_id=data['profile_id'], deleted_at=None
        ).first()
        if existing:
            return {'message': 'Member already in group'}, 409
        member = GroupMember(
            group_id=group_id,
            profile_id=data['profile_id'],
            role_id=data.get('role_id')
        )
        db.session.add(member)
        db.session.commit()
        return {'message': 'Member added', 'id': str(member.id)}, 201


@group_ns.route('/<string:group_id>/members/<string:member_id>')
class GroupMemberDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id, member_id):
        """Remove a member from a group"""
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id, deleted_at=None).first()
        if not member:
            return {'message': 'Member not found'}, 404
        member.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Member removed'}, 200
