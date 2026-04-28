from datetime import datetime, timezone
from db import db
from db.models import TransactionType


class TransactionTypeService:

    @staticmethod
    def get_all():
        items = TransactionType.query.filter_by(deleted_at=None).all()
        return [_serialize(t) for t in items]

    @staticmethod
    def get_by_id(type_id):
        return TransactionType.query.filter_by(id=type_id, deleted_at=None).first()

    @staticmethod
    def create(data):
        item = TransactionType(
            name=data['name'],
            status=data.get('status', 'ACTIVE'),
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(type_id, data):
        item = TransactionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['name', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(type_id):
        item = TransactionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item


def _serialize(t):
    return {
        'id': str(t.id),
        'name': t.name,
        'status': t.status,
        'created_at': str(t.created_at),
    }
