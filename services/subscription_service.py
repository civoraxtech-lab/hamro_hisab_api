from datetime import datetime, timezone
from db import db
from db.models import Subscription


class SubscriptionService:

    @staticmethod
    def get_all():
        items = Subscription.query.filter_by(deleted_at=None).all()
        return [_serialize(s) for s in items]

    @staticmethod
    def get_by_user(user_id):
        items = Subscription.query.filter_by(user_id=user_id, deleted_at=None).all()
        return [_serialize(s) for s in items]

    @staticmethod
    def get_by_id(subscription_id):
        return Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()

    @staticmethod
    def create(data):
        item = Subscription(
            user_id=data['user_id'],
            type_id=data['type_id'],
            expiry=datetime.fromisoformat(data['expiry']),
            total_amount=data['total_amount'],
            paid_amount=data['paid_amount'],
            discount=data.get('discount'),
            is_percent=data.get('is_percent', False),
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(subscription_id, data):
        item = Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()
        if not item:
            return None
        if 'expiry' in data:
            item.expiry = datetime.fromisoformat(data['expiry'])
        for field in ['total_amount', 'paid_amount', 'discount', 'is_percent']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(subscription_id):
        item = Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item


def _serialize(s):
    return {
        'id': str(s.id),
        'user_id': str(s.user_id),
        'type_id': str(s.type_id),
        'expiry': str(s.expiry) if s.expiry else None,
        'total_amount': float(s.total_amount) if s.total_amount else None,
        'paid_amount': float(s.paid_amount) if s.paid_amount else None,
        'discount': float(s.discount) if s.discount else None,
        'is_percent': s.is_percent,
        'created_at': str(s.created_at),
    }
