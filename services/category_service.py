from datetime import datetime, timezone
from db import db
from db.models import Category


class CategoryService:

    @staticmethod
    def get_all(include_deleted=False):
        q = Category.query
        if not include_deleted:
            q = q.filter_by(deleted_at=None)
        return [c.to_dict for c in q.all()]

    @staticmethod
    def get_by_id(category_id, include_deleted=False):
        q = Category.query.filter_by(id=category_id)
        if not include_deleted:
            q = q.filter_by(deleted_at=None)
        return q.first()

    @staticmethod
    def create(data, user_id):
        item = Category(
            name=data['name'],
            icon=data.get('icon'),
            iconColor=data.get('iconColor'),
            is_default=data.get('is_default', False),
            created_by=user_id,
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(category_id, data):
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['name', 'icon', 'iconColor', 'is_default']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(category_id):
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def restore(category_id):
        item = Category.query.filter_by(id=category_id).first()
        if not item or not item.deleted_at:
            return None
        item.deleted_at = None
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item
