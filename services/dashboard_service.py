from db import db
from db.models import Transaction, Liability, Group, GroupMember, Profile
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone


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
        alerts = _compute_alerts(profile.id)

        return {
            'profile': {'id': str(profile.id), 'name': profile.name},
            'totals': totals,
            # flat fields the Flutter app expects:
            'net_balance': totals['net_balance'],
            'you_owe': totals['you_owe'],
            'youll_get': totals['youll_get'],
            'monthly_spending': totals['monthly_spending'],
            'recent_transactions': [_serialize_tx(t) for t in recent_transactions],
            'recent_groups': [_serialize_group(g) for g in recent_groups],
            'alerts': alerts,
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

    monthly_spending = _compute_monthly_spending(profile_id)

    return {
        'total_owed': round(total_owed, 2),
        'total_receivable': round(total_receivable, 2),
        'net_balance': round(total_receivable - total_owed, 2),
        'you_owe': round(total_owed, 2),
        'youll_get': round(total_receivable, 2),
        'monthly_spending': monthly_spending,
    }


def _compute_monthly_spending(profile_id):
    now = datetime.now(timezone.utc)
    try:
        monthly_txs = (
            Transaction.query
            .join(Liability, Transaction.id == Liability.transaction_id)
            .filter(
                Liability.profile_id == profile_id,
                Liability.deleted_at == None,
                Transaction.deleted_at == None,
                db.extract('year', Transaction.date) == now.year,
                db.extract('month', Transaction.date) == now.month,
            )
            .all()
        )
        return round(sum(float(t.amount or 0) for t in monthly_txs), 2)
    except Exception:
        return 0.0


def _compute_alerts(profile_id):
    alerts = []
    try:
        pending = (
            Liability.query
            .filter(
                Liability.profile_id == profile_id,
                Liability.deleted_at == None,
                Liability.initial_payer == False,
            )
            .options(joinedload(Liability.transaction))
            .limit(10)
            .all()
        )
        for l in pending:
            remaining = float(l.settlement_amount or 0) - float(l.settled_amount or 0)
            if remaining > 0:
                tx = l.transaction
                tx_title = tx.title if tx else 'a transaction'
                alerts.append({
                    'id': str(l.id),
                    'title': f'You owe NPR {remaining:.0f}',
                    'subtitle': f'For {tx_title}',
                    'time': tx.date.isoformat() if tx and tx.date else '',
                    'type': 'settle_reminder',
                })
    except Exception:
        pass
    return alerts


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
