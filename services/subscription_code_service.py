from datetime import datetime, timezone
from db import db
from db.models import SubscriptionCode


class SubscriptionCodeService:

    @staticmethod
    def get_all():
        items = SubscriptionCode.query.filter_by(deleted_at=None).all()
        return [_serialize(s) for s in items]

    @staticmethod
    def get_by_id(code_id):
        return SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()

    @staticmethod
    def create(data):
        item = SubscriptionCode(
            code=data['code'],
            discount=data.get('discount'),
            is_percent=data.get('is_percent', False),
            status=data.get('status', 'ACTIVE'),
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(code_id, data):
        item = SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['code', 'discount', 'is_percent', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(code_id):
        item = SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item


def _serialize(s):
    return {
        'id': str(s.id),
        'code': s.code,
        'discount': float(s.discount) if s.discount else None,
        'is_percent': s.is_percent,
        'status': s.status,
        'created_at': str(s.created_at),
    }
