from datetime import datetime, timezone
from db import db
from db.models import Profile


def _serialize(p):
    return {
        'id': str(p.id),
        'user_id': str(p.user_id),
        'name': p.name,
        'is_default': p.is_default,
        'created_at': str(p.created_at),
    }


class ProfileService:

    @staticmethod
    def get_by_user(user_id):
        items = Profile.query.filter_by(user_id=user_id, deleted_at=None).all()
        return [_serialize(p) for p in items]

    @staticmethod
    def get_by_id(profile_id, user_id):
        return Profile.query.filter_by(
            id=profile_id, user_id=user_id, deleted_at=None
        ).first()

    @staticmethod
    def create(data, user_id):
        item = Profile(
            user_id=user_id,
            name=data['name'],
            is_default=data.get('is_default', False),
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(profile_id, user_id, data):
        item = Profile.query.filter_by(
            id=profile_id, user_id=user_id, deleted_at=None
        ).first()
        if not item:
            return None
        for field in ['name', 'is_default']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(profile_id, user_id):
        item = Profile.query.filter_by(
            id=profile_id, user_id=user_id, deleted_at=None
        ).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def serialize(p):
        return _serialize(p)
