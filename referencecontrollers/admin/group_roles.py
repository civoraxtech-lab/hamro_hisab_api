
from db import db
from db.models import GroupRole
from sqlalchemy.orm import joinedload
from datetime import datetime,timezone

class GroupRoleController:
    @staticmethod
    def index():
        items = GroupRole.query.filter_by(deleted_at=None).all()
       
        return [gr.to_dict for gr in items], 200
        
    @staticmethod
    def create(data):
        item = GroupRole(
            name=data['name'], 
            status=data.get('status')
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def show(role_id):
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return None
        return item.to_dict, 200
    
    @staticmethod
    def update(role_id, data):
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return None
        fields = ['name', 'status']
        for field in fields:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return item

    @staticmethod
    def delete(role_id):
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item.to_dict
        