from db import db
from db.models import Liability
from sqlalchemy.orm import joinedload
from datetime import datetime,timezone

class LiabilityController:
    @staticmethod
    def index():
        items = Liability.query.options( 
            joinedload(Liability.profile),
            joinedload(Liability.transaction)
            ).filter_by(deleted_at=None).all()
       
        return [l.to_dict for l in items], 200
        
    @staticmethod
    def create(data):
        item = Liability(
            transaction_id=data['transaction_id'],
            profile_id=data['profile_id'],
            settlement_amount=data['settlement_amount'],
            initial_payer=data.get('initial_payer', False),
            is_verified=data.get('is_verified', False)
        )
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def show(liability_id):
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return None
        return item.to_dict, 200
    
    @staticmethod
    def update(liability_id, data):
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return None
        fields = ['settled_amount', 'is_verified']
        for field in fields:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return item

    @staticmethod
    def delete(liability_id):
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return None
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return item.to_dict
        