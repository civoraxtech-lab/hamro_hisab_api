from datetime import datetime, timezone
from db import db
from db.models import Group, GroupMember, GroupRole
from db.models.group_invitations import GroupInvitation


class InvitationService:

    @staticmethod
    def create(group_id, invited_user_id, invited_by_profile_id):
        """Create a pending invitation. Raises ValueError if already pending/accepted."""
        existing = GroupInvitation.query.filter_by(
            group_id=group_id,
            invited_user_id=invited_user_id,
            status='pending',
            deleted_at=None,
        ).first()
        if existing:
            raise ValueError('User already has a pending invitation to this group')

        # Also reject if already an active member
        from db.models import Profile
        profiles = Profile.query.filter_by(user_id=invited_user_id, deleted_at=None).all()
        profile_ids = [p.id for p in profiles]
        if profile_ids:
            already_member = GroupMember.query.filter(
                GroupMember.group_id == group_id,
                GroupMember.profile_id.in_(profile_ids),
                GroupMember.deleted_at == None,
            ).first()
            if already_member:
                raise ValueError('User is already a member of this group')

        inv = GroupInvitation(
            group_id=group_id,
            invited_user_id=invited_user_id,
            invited_by_profile_id=invited_by_profile_id,
            status='pending',
        )
        db.session.add(inv)
        db.session.commit()
        return inv

    @staticmethod
    def get_pending_for_user(user_id):
        """Return all pending invitations for a user, enriched with group/inviter info."""
        from db.models import User, Profile
        rows = (
            db.session.query(GroupInvitation, Group)
            .join(Group, GroupInvitation.group_id == Group.id)
            .filter(
                GroupInvitation.invited_user_id == user_id,
                GroupInvitation.status == 'pending',
                GroupInvitation.deleted_at == None,
                Group.deleted_at == None,
            )
            .order_by(GroupInvitation.created_at.desc())
            .all()
        )

        result = []
        for inv, group in rows:
            inviter_name = None
            if inv.invited_by_profile_id:
                profile = Profile.query.get(inv.invited_by_profile_id)
                if profile:
                    user = User.query.get(profile.user_id)
                    if user:
                        inviter_name = f'{user.firstname} {user.lastname}'

            result.append({
                'id': str(inv.id),
                'group_id': str(group.id),
                'group_name': group.name,
                'group_icon': group.icon,
                'group_description': group.description,
                'invited_by_name': inviter_name,
                'created_at': str(inv.created_at),
            })
        return result

    @staticmethod
    def accept(invitation_id, user_id, profile_id):
        """Accept an invitation: create GroupMember and mark invitation accepted."""
        inv = GroupInvitation.query.filter_by(
            id=invitation_id,
            invited_user_id=user_id,
            status='pending',
            deleted_at=None,
        ).first()
        if not inv:
            return {'message': 'Invitation not found or already processed'}, 404

        # Verify the profile belongs to this user
        from db.models import Profile
        profile = Profile.query.filter_by(
            id=profile_id, user_id=user_id, deleted_at=None
        ).first()
        if not profile:
            return {'message': 'Profile not found'}, 404

        member_role = GroupRole.query.filter_by(name='MEMBER', deleted_at=None).first()
        member = GroupMember(
            group_id=inv.group_id,
            profile_id=profile_id,
            role_id=member_role.id if member_role else None,
        )
        db.session.add(member)

        inv.status = 'accepted'
        inv.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Invitation accepted', 'member_id': str(member.id)}, 200

    @staticmethod
    def reject(invitation_id, user_id):
        """Reject an invitation."""
        inv = GroupInvitation.query.filter_by(
            id=invitation_id,
            invited_user_id=user_id,
            status='pending',
            deleted_at=None,
        ).first()
        if not inv:
            return {'message': 'Invitation not found or already processed'}, 404

        inv.status = 'rejected'
        inv.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Invitation rejected'}, 200
