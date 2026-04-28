from datetime import datetime, timezone
from db import db
from db.models import Group, GroupMember, GroupRole


class GroupService:

    @staticmethod
    def get_all(include_deleted=False):
        q = Group.query
        if not include_deleted:
            q = q.filter_by(deleted_at=None)
        return [g.to_dict for g in q.all()]

    @staticmethod
    def get_by_profile(profile_id):
        group_ids = (
            db.session.query(GroupMember.group_id)
            .filter_by(profile_id=profile_id, deleted_at=None)
            .subquery()
        )
        items = Group.query.filter(
            Group.id.in_(group_ids), Group.deleted_at == None
        ).all()
        return [g.to_dict for g in items]

    @staticmethod
    def get_by_id(group_id):
        return Group.query.filter_by(id=group_id, deleted_at=None).first()

    @staticmethod
    def create(data, profile):
        item = Group(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            require_verification=data.get('require_verification', True),
            created_by=profile.id,
        )
        db.session.add(item)
        db.session.flush()

        role = GroupRole.query.filter_by(name='ADMIN', deleted_at=None).first()
        member = GroupMember(
            profile_id=profile.id,
            group_id=item.id,
            role_id=role.id if role else None,
        )
        db.session.add(member)
        db.session.commit()
        return item

    @staticmethod
    def update(group_id, data):
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return None
        for field in ['name', 'description', 'icon', 'require_verification']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def soft_delete(group_id):
        item = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item

    @staticmethod
    def get_members(group_id):
        from db.models import Profile, User, GroupRole as GR
        rows = (
            db.session.query(GroupMember, Profile, User, GR)
            .join(Profile, GroupMember.profile_id == Profile.id)
            .join(User, Profile.user_id == User.id)
            .outerjoin(GR, GroupMember.role_id == GR.id)
            .filter(GroupMember.group_id == group_id, GroupMember.deleted_at == None)
            .all()
        )
        result = []
        for m, profile, user, role in rows:
            result.append({
                'id': str(m.id),
                'profile_id': str(m.profile_id),
                'user_id': str(user.id),
                'firstname': user.firstname,
                'lastname': user.lastname,
                'image': user.image,
                'role': role.name if role else None,
                'joined_at': str(m.created_at),
            })
        return result

    @staticmethod
    def add_member(group_id, data):
        existing = GroupMember.query.filter_by(
            group_id=group_id, profile_id=data['profile_id'], deleted_at=None
        ).first()
        if existing:
            return existing, 409
        item = GroupMember(
            group_id=group_id,
            profile_id=data['profile_id'],
            role_id=data.get('role_id'),
        )
        db.session.add(item)
        db.session.commit()
        return item, 201

    @staticmethod
    def invite_user(group_id, user_id):
        from db.models import Profile
        profile = Profile.query.filter_by(user_id=user_id, is_default=True, deleted_at=None).first()
        if not profile:
            profile = Profile.query.filter_by(user_id=user_id, deleted_at=None).first()
        if not profile:
            return None, 404
        member_role = GroupRole.query.filter_by(name='MEMBER', deleted_at=None).first()
        return GroupService.add_member(group_id, {
            'profile_id': str(profile.id),
            'role_id': str(member_role.id) if member_role else None,
        })

    @staticmethod
    def leave_group(group_id, profile_id):
        member = GroupMember.query.filter_by(
            group_id=group_id, profile_id=profile_id, deleted_at=None
        ).first()
        if not member:
            return None
        member.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return member

    @staticmethod
    def remove_member(group_id, member_id):
        item = GroupMember.query.filter_by(
            id=member_id, group_id=group_id, deleted_at=None
        ).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item
