from datetime import datetime, timezone
from db import db
from db.models import Transaction, Liability


def create_transaction(profile, data):
    if not data.get('title') or not data.get('amount'):
        raise ValueError("title and amount are required")

    tx = Transaction(
        title=data['title'],
        amount=data['amount'],
        category_id=data.get('category_id'),
        group_id=data.get('group_id'),
        type_id=data.get('type_id'),
        description=data.get('description'),
        date=datetime.fromisoformat(data['date']) if data.get('date') else datetime.now(timezone.utc),
        profile_id=profile.id,
    )
    db.session.add(tx)
    db.session.flush()

    db.session.add(Liability(
        transaction_id=tx.id,
        profile_id=profile.id,
        settlement_amount=data['amount'],
        settled_amount=data['amount'],
        initial_payer=True,
    ))
    db.session.commit()
    return tx


def update_transaction(transaction_id, profile_id, data):
    tx = Transaction.query.filter_by(id=transaction_id, profile_id=profile_id, deleted_at=None).first()
    if not tx:
        return None

    if 'date' in data:
        tx.date = datetime.fromisoformat(data['date'])
    for field in ['title', 'amount', 'category_id', 'type_id', 'description']:
        if field in data:
            setattr(tx, field, data[field])
    tx.updated_at = datetime.now(timezone.utc)

    if 'amount' in data:
        liability = Liability.query.filter_by(
            transaction_id=transaction_id,
            initial_payer=True,
            deleted_at=None
        ).first()
        if liability:
            liability.settlement_amount = data['amount']
            liability.settled_amount = data['amount']
            liability.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return tx


def delete_transaction(transaction_id, profile_id):
    tx = Transaction.query.filter_by(id=transaction_id, profile_id=profile_id, deleted_at=None).first()
    if not tx:
        return False

    now = datetime.now(timezone.utc)
    tx.deleted_at = now

    Liability.query.filter_by(transaction_id=transaction_id, deleted_at=None).update(
        {'deleted_at': now}
    )

    db.session.commit()
    return True
