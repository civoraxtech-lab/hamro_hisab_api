from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Group, GroupMember
from utils.decorators import token_required
from controllers.member.group import GroupController

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


# --- Group CRUD ---

@group_ns.route('/')
class GroupList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self):
        items = GroupController.index()
        return items, 200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(create_group_model)
    @token_required
    def post(self):
        item = GroupController.create(request.json)
        return {'message': 'Group created', 'id': str(item.id)}, 201
        


@group_ns.route('/<string:group_id>')
class GroupDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        item = GroupController.show(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
        
        return item,200

    @group_ns.doc(security='Bearer')
    @group_ns.expect(update_group_model)
    @token_required
    def put(self, group_id):
        updated_item = GroupController.update(group_id, request.json)
        if not updated_item:
            return {'message': 'Group not found'}, 404
            
        return {'message': 'Group updated'}, 200

    

    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id):
        item = GroupController.delete(group_id)
        if not item:
            return {'message': 'Group not found'}, 404
            
        return {'message': 'Group deleted'}, 200


# --- Group Members ---

@group_ns.route('/<string:group_id>/members')
class GroupMemberList(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def get(self, group_id):
        items = GroupController.members(group_id)
        return items, 200
       

    @group_ns.doc(security='Bearer')
    @group_ns.expect(add_member_model)
    @token_required
    def post(self, group_id):
        item, status_code = GroupController.createMember(group_id,request.json)
        if status_code == 409:
            return {
                'message': 'Member already exists in this group',
                'id': str(item.id)
            }, 409
        return {
            'message': 'Member added successfully',
            'id': str(item.id) # 'result' is the new item
        }, 201
        

@group_ns.route('/<string:group_id>/members/<string:member_id>')
class GroupMemberDetail(Resource):
    @group_ns.doc(security='Bearer')
    @token_required
    def delete(self, group_id, member_id):
        item = GroupController.deleteMember(group_id,member_id)
        if not item:
            return {'message': 'Member not found'}, 404
            
        return {'message': 'Member deleted'}, 200