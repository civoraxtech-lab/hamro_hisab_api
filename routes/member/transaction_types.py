from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, TransactionType
from utils.decorators import token_required

transaction_types_ns = Namespace(
    'transaction-types',
    description='Transaction type operations',
    path='/api/transaction-types'
)

create_model = transaction_types_ns.model('CreateTransactionType', {
    'name': fields.String(required=True, example='EXPENSE'),
    'status': fields.String(example='ACTIVE'),
})

update_model = transaction_types_ns.model('UpdateTransactionType', {
    'name': fields.String(example='EXPENSE'),
    'status': fields.String(example='ACTIVE'),
})


def serialize(t):
    return {
        'id': str(t.id),
        'name': t.name,
        'status': t.status,
        'created_at': str(t.created_at),
    }


@transaction_types_ns.route('/')
class TransactionTypeList(Resource):
    @transaction_types_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active transaction types"""
        items = TransactionType.query.filter_by(deleted_at=None).all()
        return [serialize(t) for t in items], 200

    @transaction_types_ns.doc(security='Bearer')
    @transaction_types_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a transaction type"""
        data = request.json
        item = TransactionType(
            name=data['name'],
            status=data.get('status', 'ACTIVE'),
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Transaction type created', 'id': str(item.id)}, 201


@transaction_types_ns.route('/<string:type_id>')
class TransactionTypeDetail(Resource):
    @transaction_types_ns.doc(security='Bearer')
    @token_required
    def get(self, type_id):
        """Get a transaction type by ID"""
        item = TransactionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction type not found'}, 404
        return serialize(item), 200

    @transaction_types_ns.doc(security='Bearer')
    @transaction_types_ns.expect(update_model)
    @token_required
    def put(self, type_id):
        """Update a transaction type"""
        item = TransactionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction type not found'}, 404
        data = request.json
        for field in ['name', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction type updated'}, 200

    @transaction_types_ns.doc(security='Bearer')
    @token_required
    def delete(self, type_id):
        """Soft-delete a transaction type"""
        item = TransactionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction type not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction type deleted'}, 200
