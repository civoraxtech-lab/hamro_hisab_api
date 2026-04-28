from datetime import datetime, timezone
from db import db
from db.models import Transaction, Liability


def create_transaction(profile, user, data):
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
        created_by=user.id,
    )
    db.session.add(tx)
    db.session.flush()

    liability = Liability(
        transaction_id=tx.id,
        profile_id=profile.id,
        settlement_amount=data['amount'],
        settled_amount=0,
        initial_payer=True,
    )
    db.session.add(liability)
    db.session.commit()
    return tx
