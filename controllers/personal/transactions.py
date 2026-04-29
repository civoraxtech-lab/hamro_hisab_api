from db import db
from db.models import Transaction, Liability
from datetime import datetime
import uuid

class TransactionController:
    @staticmethod
    def create(user, data):
        if not data.get('amount') or not data.get('title'):
            return {"error": "Amount and Title are required"}, 400

        new_tx = Transaction(
            id=uuid.uuid4(),
            title=data.get('title'),
            amount=data.get('amount'),
            category_id=data.get('category_id'),
            date=datetime.fromisoformat(data.get('date', datetime.utcnow().isoformat())),
            description=data.get('description', "")
        )
        db.session.add(new_tx)
        db.session.flush()
        new_liability = Liability(
            id=uuid.uuid4(),
            transaction_id=new_tx.id,
            user_id=user.id,
            settlement_amount=data.get('amount'),
            settled_amount=data.get('amount'),
            initial_payer=True
        )
        
        db.session.add(new_liability)
        
        try:
            db.session.commit()
            return {"message": "Transaction added successfully", "id": str(new_tx.id)}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500