from datetime import datetime, timezone
from db import db
from db.models import SubscriptionType


class SubscriptionTypeService:

    @staticmethod
    def get_all():
        items = SubscriptionType.query.filter_by(deleted_at=None).all()
        return [_serialize(s) for s in items]

    @staticmethod
    def get_by_id(type_id):
        return SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()

    @staticmethod
    def create(data):
        item = SubscriptionType(
            name=data['name'],
            price=data['price'],
            status=data.get('status', 'ACTIVE'),
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(type_id, data):
        item = SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['name', 'price', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(type_id):
        item = SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item


def _serialize(s):
    return {
        'id': str(s.id),
        'name': s.name,
        'price': float(s.price),
        'status': s.status,
        'created_at': str(s.created_at),
    }
