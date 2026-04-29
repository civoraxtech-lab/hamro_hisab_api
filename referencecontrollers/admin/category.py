
from db import db
from db.models import Category
from sqlalchemy.orm import joinedload
from datetime import datetime,timezone

class CategoryController:
    @staticmethod
    def index():
        
        items = Category.query.filter_by(deleted_at=None).all()
       
        return [c.to_dict for c in items], 200
        
    @staticmethod
    def create(data, user_id):
        item = Category(
            name=data['name'],
            icon=data.get('icon'),
            iconColor=data.get('iconColor'),
            is_default=data.get('is_default', False),
            created_by=user_id
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def show(category_id):
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return None
        return item.to_dict, 200
    
    @staticmethod
    def update(category_id, data):
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return None
        fields = ['name', 'icon', 'iconColor', 'is_default']
        for field in fields:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return item

    @staticmethod
    def delete(category_id):
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return None

        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item.to_dict
        