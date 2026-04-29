from datetime import datetime, timezone
from db import db
from db.models import GroupRole


class GroupRoleService:

    @staticmethod
    def get_all():
        items = GroupRole.query.filter_by(deleted_at=None).all()
        return [r.to_dict for r in items]

    @staticmethod
    def get_by_id(role_id):
        return GroupRole.query.filter_by(id=role_id, deleted_at=None).first()

    @staticmethod
    def create(data):
        item = GroupRole(name=data['name'], status=data.get('status', 'ACTIVE'))
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update(role_id, data):
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['name', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(role_id):
        item = GroupRole.query.filter_by(id=role_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item
