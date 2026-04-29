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
    def join_group_by_qr(group_id, profile_id):
        group = Group.query.filter_by(id=group_id, deleted_at=None).first()
        if not group:
            return {'message': 'Group not found'}, 404
        existing = GroupMember.query.filter_by(
            group_id=group_id, profile_id=profile_id, deleted_at=None
        ).first()
        if existing:
            return {'message': 'You are already a member of this group'}, 409
        member_role = GroupRole.query.filter_by(name='MEMBER', deleted_at=None).first()
        if not member_role:
            return {'message': 'Member role not configured'}, 500
        new_member = GroupMember(
            group_id=group_id,
            profile_id=profile_id,
            role_id=member_role.id,
        )
        db.session.add(new_member)
        db.session.commit()
        return {'message': f'Joined {group.name} successfully'}, 201

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
                    'verification_status': l.verification_status or 'approved',
                    'verified_via': l.verified_via,
                    'verified_at': str(l.verified_at) if l.verified_at else None,
                })

            result.append({
                'id': str(tx.id),
                'title': tx.title,
                'amount': float(tx.amount),
                'description': tx.description,
                'date': str(tx.date or tx.created_at),
                'type_id': str(tx.type_id) if tx.type_id else None,
                'category_id': str(tx.category_id) if tx.category_id else None,
                'status': tx.status or 'approved',
                'initiator_profile_id': str(tx.profile_id) if tx.profile_id else None,
                'paid_by': paid_by,
                'liabilities': liab_list,
            })
        return result

    @staticmethod
    def _build_liabilities(tx_id, paid_by_amounts, member_profile_ids, split_method, data):
        from db.models import Liability
        total = float(tx_id.amount if hasattr(tx_id, 'amount') else 0)
        return []  # placeholder; see _compute_shares

    @staticmethod
    def _compute_shares(total, member_profile_ids, split_method, data):
        n = len(member_profile_ids)
        if n == 0:
            return {}
        if split_method == 'exact':
            exact = data.get('exact_amounts') or {}
            return {str(pid): float(exact.get(str(pid), 0)) for pid in member_profile_ids}
        # equal (default)
        shares = {str(pid): round(total / n, 2) for pid in member_profile_ids}
        diff = round(total - sum(shares.values()), 2)
        shares[str(member_profile_ids[0])] = round(shares[str(member_profile_ids[0])] + diff, 2)
        return shares

    @staticmethod
    def create_group_transaction(group_id, data, current_profile):
        from db.models import Transaction, Liability, Group

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

        if not paid_by_amounts and paid_by_profile_id:
            paid_by_amounts = {str(paid_by_profile_id): float(amount)}

        if not paid_by_amounts:
            return {'message': 'paid_by_amounts is required'}, 400
        if not member_profile_ids:
            return {'message': 'member_profile_ids is required'}, 400

        paid_by_amounts = {str(k): float(v) for k, v in paid_by_amounts.items()}

        group = Group.query.filter_by(id=group_id, deleted_at=None).first()
        require_verification = group.require_verification if group else False
        tx_status = 'pending' if require_verification else 'approved'

        tx = Transaction(
            title=title,
            amount=amount,
            group_id=group_id,
            description=data.get('description'),
            type_id=data.get('type_id'),
            category_id=data.get('category_id'),
            date=datetime.fromisoformat(data['date']) if data.get('date') else datetime.now(timezone.utc),
            profile_id=current_profile.id,
            status=tx_status,
        )
        db.session.add(tx)
        db.session.flush()

        shares = GroupService._compute_shares(float(amount), member_profile_ids, split_method, data)

        initiator_id = str(current_profile.id)
        for pid in member_profile_ids:
            settled = paid_by_amounts.get(str(pid), 0.0)
            is_initiator = str(pid) == initiator_id
            # initiator is auto-approved; others are pending when verification required
            v_status = 'approved' if (not require_verification or is_initiator) else 'pending'
            db.session.add(Liability(
                transaction_id=tx.id,
                profile_id=pid,
                settlement_amount=shares.get(str(pid), 0),
                settled_amount=settled,
                initial_payer=settled > 0,
                verification_status=v_status,
            ))

        db.session.commit()
        return {'message': 'Transaction created', 'id': str(tx.id)}, 201

    @staticmethod
    def verify_liability(group_id, tx_id, liability_id, data, current_profile):
        from db.models import Transaction, Liability, Profile, User

        action = (data.get('action') or '').strip().lower()
        code = (data.get('code') or '').strip()

        if action not in ('approve', 'reject'):
            return {'message': 'action must be approve or reject'}, 400

        tx = Transaction.query.filter_by(id=tx_id, group_id=group_id, deleted_at=None).first()
        if not tx:
            return {'message': 'Transaction not found'}, 404
        if tx.status != 'pending':
            return {'message': 'Transaction is not pending verification'}, 400

        liability = Liability.query.filter_by(
            id=liability_id, transaction_id=tx_id, deleted_at=None
        ).first()
        if not liability:
            return {'message': 'Liability not found'}, 404
        if liability.verification_status != 'pending':
            return {'message': 'This liability has already been verified'}, 400

        # Initiator cannot verify their own liability via this endpoint
        if str(liability.profile_id) == str(tx.profile_id):
            return {'message': 'Initiator liability is auto-approved'}, 400

        verified_via = 'live'
        if code:
            # Offline: validate the unique code against the liability owner's user record
            profile = Profile.query.get(liability.profile_id)
            if not profile:
                return {'message': 'Profile not found'}, 404
            user = User.query.get(profile.user_id)
            if not user or user.code != code:
                return {'message': 'Invalid code'}, 400
            verified_via = 'code'
        else:
            # Live: only the liability owner can approve/reject their own entry
            if str(liability.profile_id) != str(current_profile.id):
                return {'message': 'You can only verify your own liability without a code'}, 403

        new_status = 'approved' if action == 'approve' else 'rejected'
        liability.verification_status = new_status
        liability.verified_via = verified_via
        liability.verified_at = datetime.now(timezone.utc)
        liability.updated_at = datetime.now(timezone.utc)

        # Recompute transaction status based on all non-initiator liabilities
        all_liabs = Liability.query.filter_by(transaction_id=tx_id, deleted_at=None).all()
        non_initiator = [l for l in all_liabs if str(l.profile_id) != str(tx.profile_id)]

        if any(l.verification_status == 'rejected' for l in non_initiator):
            tx.status = 'rejected'
        elif all(l.verification_status == 'approved' for l in non_initiator):
            tx.status = 'approved'

        tx.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': f'Liability {new_status}', 'transaction_status': tx.status}, 200

    @staticmethod
    def update_group_transaction(group_id, tx_id, data, current_profile):
        from db.models import Transaction, Liability, Group

        tx = Transaction.query.filter_by(
            id=tx_id, group_id=group_id, deleted_at=None
        ).first()
        if not tx:
            return {'message': 'Transaction not found'}, 404

        if tx.status == 'pending':
            return {'message': 'Cannot edit a transaction that is pending verification'}, 400

        title = (data.get('title') or '').strip()
        amount = data.get('amount')
        paid_by_amounts = data.get('paid_by_amounts') or {}
        member_profile_ids = data.get('member_profile_ids') or []
        split_method = (data.get('split_method') or 'equal').lower()

        if not title:
            return {'message': 'title is required'}, 400
        if not amount or float(amount) <= 0:
            return {'message': 'amount must be positive'}, 400
        if not paid_by_amounts:
            return {'message': 'paid_by_amounts is required'}, 400
        if not member_profile_ids:
            return {'message': 'member_profile_ids is required'}, 400

        paid_by_amounts = {str(k): float(v) for k, v in paid_by_amounts.items()}

        group = Group.query.filter_by(id=group_id, deleted_at=None).first()
        require_verification = group.require_verification if group else False

        tx.title = title
        tx.amount = float(amount)
        tx.description = data.get('description')
        if data.get('type_id') is not None:
            tx.type_id = data['type_id']
        if data.get('category_id') is not None:
            tx.category_id = data['category_id']
        if data.get('date'):
            tx.date = datetime.fromisoformat(data['date'])
        tx.updated_at = datetime.now(timezone.utc)

        # Re-trigger verification: edited transactions go back to pending
        tx.status = 'pending' if require_verification else 'approved'
        # Update the initiator to the editor so the sheet shows correctly
        tx.profile_id = current_profile.id

        # Soft-delete existing liabilities and recreate
        existing_liabs = Liability.query.filter_by(
            transaction_id=tx.id, deleted_at=None
        ).all()
        for l in existing_liabs:
            l.deleted_at = datetime.now(timezone.utc)

        initiator_id = str(current_profile.id)
        shares = GroupService._compute_shares(float(amount), member_profile_ids, split_method, data)
        for pid in member_profile_ids:
            settled = paid_by_amounts.get(str(pid), 0.0)
            is_initiator = str(pid) == initiator_id
            v_status = 'approved' if (not require_verification or is_initiator) else 'pending'
            db.session.add(Liability(
                transaction_id=tx.id,
                profile_id=pid,
                settlement_amount=shares.get(str(pid), 0),
                settled_amount=settled,
                initial_payer=settled > 0,
                verification_status=v_status,
            ))

        db.session.commit()
        return {'message': 'Transaction updated', 'id': str(tx.id)}, 200

    @staticmethod
    def delete_group_transaction(group_id, tx_id, current_profile):
        from db.models import Transaction, Liability, GroupMember, GroupRole

        tx = Transaction.query.filter_by(
            id=tx_id, group_id=group_id, deleted_at=None
        ).first()
        if not tx:
            return {'message': 'Transaction not found'}, 404

        is_initiator = str(tx.profile_id) == str(current_profile.id)

        if not is_initiator:
            admin_role = GroupRole.query.filter_by(name='ADMIN', deleted_at=None).first()
            is_admin = admin_role and GroupMember.query.filter_by(
                group_id=group_id,
                profile_id=current_profile.id,
                role_id=admin_role.id,
                deleted_at=None,
            ).first() is not None
            if not is_admin:
                return {'message': 'Only the transaction initiator or a group admin can delete this transaction'}, 403

        liabs = Liability.query.filter_by(transaction_id=tx.id, deleted_at=None).all()
        for l in liabs:
            l.deleted_at = datetime.now(timezone.utc)

        tx.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction deleted'}, 200
