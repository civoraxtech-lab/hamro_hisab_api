
from db import db
from db.models import Group, GroupMember,GroupRole
from datetime import datetime,timezone

class GroupController:
    @staticmethod
    def index(): 
        items = Group.query.filter_by(deleted_at=None).all()
        return [g.to_dict for g in items], 200
        
    @staticmethod
    def create(data):
        
        item = Group(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            require_verification=data.get('require_verification', True),
            created_by=data['profile_id']
        )
        db.session.add(item)
        db.session.flush()
        
        role = GroupRole.query.filter_by(name="ADMIN", deleted_at=None).first()
        role.to_dict
        member = GroupMember(
            profile_id=data['profile_id'],
            group_id=item.id,
            role_id=role.id
        )
        db.session.add(member)
        db.session.commit()

        return item.to_dict,201

    @staticmethod
    def show(group_id):
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return None
        return item.to_dict, 200
    
    @staticmethod
    def update(group_id, data):
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return None
        fields = ['name', 'description', 'icon', 'require_verification']
        for field in fields:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return item

    @staticmethod
    def delete(group_id):
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item.to_dict

    @staticmethod
    def members(group_id):
        items = GroupMember.query.filter_by(group_id=group_id, deleted_at=None).all()
        return [m.to_dict for m in items], 200


    @staticmethod
    def createMember(group_id, data):
        existing = GroupMember.query.filter_by(
            group_id=group_id, profile_id=data['profile_id'], deleted_at=None
        ).first()
        if existing:
            return existing.to_dict, 409
        item = GroupMember(
            group_id=group_id,
            profile_id=data['profile_id'],
            role_id=data['role_id']
        )
        db.session.add(item)
        db.session.commit()
        return item, 201

    @staticmethod
    def deleteMember(group_id, member_id):
        item = GroupMember.query.filter_by(id=member_id, group_id=group_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item.to_dict

        