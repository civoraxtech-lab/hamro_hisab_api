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
    def invite_user(group_id, user_id, invited_by_profile_id=None):
        from db.models import User
        from services.invitation_service import InvitationService
        user = User.query.filter_by(id=user_id, deleted_at=None).first()
        if not user:
            return None, 404
        try:
            inv = InvitationService.create(group_id, user_id, invited_by_profile_id)
            return inv, 201
        except ValueError as e:
            return {'message': str(e)}, 409

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

    # ── Group transactions ─────────────────────────────────────────────────────

    @staticmethod
    def get_transactions(group_id):
        from db.models import Transaction, Liability, Profile, User
        txs = (
            Transaction.query
            .filter_by(group_id=group_id, deleted_at=None)
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .all()
        )
        result = []
        for tx in txs:
            liabilities = Liability.query.filter_by(
                transaction_id=tx.id, deleted_at=None
            ).all()

            payer_liab = next((l for l in liabilities if l.initial_payer), None)
            paid_by = None
            if payer_liab:
                profile = Profile.query.get(payer_liab.profile_id)
                user = User.query.get(profile.user_id) if profile else None
                if user:
                    paid_by = {
                        'profile_id': str(payer_liab.profile_id),
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'image': user.image,
                    }

            liab_list = []
            for l in liabilities:
                profile = Profile.query.get(l.profile_id)
                user = User.query.get(profile.user_id) if profile else None
                liab_list.append({
                    'id': str(l.id),
                    'profile_id': str(l.profile_id),
                    'firstname': user.firstname if user else '',
                    'lastname': user.lastname if user else '',
                    'image': user.image if user else None,
                    'settlement_amount': float(l.settlement_amount or 0),
                    'settled_amount': float(l.settled_amount or 0),
                    'initial_payer': l.initial_payer,
                    'is_verified': l.is_verified,
                })

            result.append({
                'id': str(tx.id),
                'title': tx.title,
                'amount': float(tx.amount),
                'description': tx.description,
                'date': str(tx.date or tx.created_at),
                'paid_by': paid_by,
                'liabilities': liab_list,
            })
        return result

    @staticmethod
    def create_group_transaction(group_id, data, current_profile):
        from db.models import Transaction, Liability

        title = (data.get('title') or '').strip()
        amount = data.get('amount')
        paid_by_amounts = data.get('paid_by_amounts') or {}
        paid_by_profile_id = data.get('paid_by_profile_id')  # backward compat
        member_profile_ids = data.get('member_profile_ids') or []
        split_method = (data.get('split_method') or 'equal').lower()

        if not title:
            return {'message': 'title is required'}, 400
        if not amount or float(amount) <= 0:
            return {'message': 'amount must be positive'}, 400

        # Support old single-payer format for backward compatibility
        if not paid_by_amounts and paid_by_profile_id:
            paid_by_amounts = {str(paid_by_profile_id): float(amount)}

        if not paid_by_amounts:
            return {'message': 'paid_by_amounts is required'}, 400
        if not member_profile_ids:
            return {'message': 'member_profile_ids is required'}, 400

        # Normalise keys to strings
        paid_by_amounts = {str(k): float(v) for k, v in paid_by_amounts.items()}

        tx = Transaction(
            title=title,
            amount=amount,
            group_id=group_id,
            description=data.get('description'),
            date=datetime.fromisoformat(data['date']) if data.get('date') else datetime.now(timezone.utc),
            profile_id=current_profile.id,
        )
        db.session.add(tx)
        db.session.flush()

        total = float(amount)
        n = len(member_profile_ids)

        if split_method == 'equal':
            shares = {str(pid): round(total / n, 2) for pid in member_profile_ids}
            # Fix rounding: assign remainder to first payer who is also a member
            diff = round(total - sum(shares.values()), 2)
            first_payer = next(
                (pid for pid in paid_by_amounts if pid in shares),
                str(member_profile_ids[0]),
            )
            shares[first_payer] = round(shares[first_payer] + diff, 2)
        elif split_method == 'exact':
            exact = data.get('exact_amounts') or {}
            shares = {str(pid): float(exact.get(str(pid), 0)) for pid in member_profile_ids}
        else:
            shares = {str(pid): round(total / n, 2) for pid in member_profile_ids}

        for pid in member_profile_ids:
            settled = paid_by_amounts.get(str(pid), 0.0)
            db.session.add(Liability(
                transaction_id=tx.id,
                profile_id=pid,
                settlement_amount=shares.get(str(pid), 0),
                settled_amount=settled,
                initial_payer=settled > 0,
            ))

        db.session.commit()
        return {'message': 'Transaction created', 'id': str(tx.id)}, 201
