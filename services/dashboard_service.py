from db import db
from db.models import Transaction, Liability, Group, GroupMember, Profile
from sqlalchemy.orm import joinedload


class DashboardService:

    @staticmethod
    def get_summary(profile):
        recent_transactions = (
            Transaction.query
            .join(Liability, Transaction.id == Liability.transaction_id)
            .filter(
                Liability.profile_id == profile.id,
                Liability.deleted_at == None,
                Transaction.deleted_at == None,
            )
            .options(joinedload(Transaction.category), joinedload(Transaction.transaction_type))
            .order_by(Transaction.date.desc())
            .limit(5)
            .all()
        )

        group_ids = (
            db.session.query(GroupMember.group_id)
            .filter_by(profile_id=profile.id, deleted_at=None)
            .subquery()
        )
        recent_groups = (
            Group.query
            .filter(Group.id.in_(group_ids), Group.deleted_at == None)
            .order_by(Group.updated_at.desc())
            .limit(5)
            .all()
        )

        totals = _compute_totals(profile.id)

        return {
            'profile': {'id': str(profile.id), 'name': profile.name},
            'totals': totals,
            'recent_transactions': [_serialize_tx(t) for t in recent_transactions],
            'recent_groups': [_serialize_group(g) for g in recent_groups],
        }


def _compute_totals(profile_id):
    liabilities = Liability.query.filter_by(profile_id=profile_id, deleted_at=None).all()
    total_owed = sum(
        float(l.settlement_amount or 0) - float(l.settled_amount or 0)
        for l in liabilities
        if not l.initial_payer
    )
    total_receivable = sum(
        float(l.settlement_amount or 0) - float(l.settled_amount or 0)
        for l in liabilities
        if l.initial_payer
    )
    return {
        'total_owed': round(total_owed, 2),
        'total_receivable': round(total_receivable, 2),
    }


def _serialize_tx(t):
    return {
        'id': str(t.id),
        'title': t.title,
        'amount': float(t.amount),
        'date': t.date.isoformat() if t.date else None,
        'category': t.category.name if t.category else 'Uncategorized',
        'category_icon': t.category.icon if t.category else None,
        'type': t.transaction_type.name if t.transaction_type else None,
        'is_group': t.group_id is not None,
    }


def _serialize_group(g):
    return {
        'id': str(g.id),
        'name': g.name,
        'icon': g.icon,
        'description': g.description,
    }
