from datetime import datetime, timezone
from db import db
from db.models import User


def _serialize(u):
    return {
        'id': str(u.id),
        'firstname': u.firstname,
        'lastname': u.lastname,
        'email': u.email,
        'phone': u.phone,
        'image': u.image,
        'code': u.code,
        'created_at': str(u.created_at),
    }


class UserService:

    @staticmethod
    def get_all():
        users = User.query.filter_by(deleted_at=None).all()
        return [_serialize(u) for u in users]

    @staticmethod
    def get_by_id(user_id):
        return User.query.filter_by(id=user_id, deleted_at=None).first()

    @staticmethod
    def update(user_id, data):
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return None
        for field in ['firstname', 'lastname', 'email', 'phone', 'image']:
            if field in data:
                setattr(user, field, data[field])
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return user

    @staticmethod
    def soft_delete(user_id):
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return None
        user.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return user

    @staticmethod
    def serialize(u):
        return _serialize(u)
