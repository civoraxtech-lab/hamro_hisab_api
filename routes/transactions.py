from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, Transaction
from utils.decorators import token_required

transactions_ns = Namespace('transactions', description='Transaction operations', path='/api/transactions')

create_model = transactions_ns.model('CreateTransaction', {
    'title': fields.String(required=True, example='Dinner split'),
    'amount': fields.Float(required=True, example=1200.00),
    'category_id': fields.String(required=True, example='uuid-here'),
    'group_id': fields.String(required=True, example='uuid-here'),
    'type_id': fields.String(required=True, example='uuid-here'),
    'description': fields.String(example='Team dinner at restaurant'),
    'date': fields.String(example='2026-04-23T20:00:00')
})

update_model = transactions_ns.model('UpdateTransaction', {
    'title': fields.String(example='Dinner split'),
    'amount': fields.Float(example=1200.00),
    'category_id': fields.String(example='uuid-here'),
    'type_id': fields.String(example='uuid-here'),
    'description': fields.String(example='Team dinner at restaurant'),
    'date': fields.String(example='2026-04-23T20:00:00')
})


def serialize(t):
    return {
        'id': str(t.id),
        'title': t.title,
        'amount': float(t.amount),
        'category_id': str(t.category_id) if t.category_id else None,
        'group_id': str(t.group_id) if t.group_id else None,
        'type_id': str(t.type_id) if t.type_id else None,
        'description': t.description,
        'date': str(t.date) if t.date else None,
        'created_at': str(t.created_at)
    }


@transactions_ns.route('/')
class TransactionList(Resource):
    @transactions_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all transactions"""
        items = Transaction.query.filter_by(deleted_at=None).all()
        return [serialize(t) for t in items], 200

    @transactions_ns.doc(security='Bearer')
    @transactions_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a transaction"""
        data = request.json
        item = Transaction(
            title=data['title'],
            amount=data['amount'],
            category_id=data['category_id'],
            group_id=data['group_id'],
            type_id=data['type_id'],
            description=data.get('description'),
            date=datetime.fromisoformat(data['date']) if data.get('date') else datetime.now(timezone.utc)
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Transaction created', 'id': str(item.id)}, 201


@transactions_ns.route('/<string:transaction_id>')
class TransactionDetail(Resource):
    @transactions_ns.doc(security='Bearer')
    @token_required
    def get(self, transaction_id):
        """Get a transaction by ID"""
        item = Transaction.query.filter_by(id=transaction_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction not found'}, 404
        return serialize(item), 200

    @transactions_ns.doc(security='Bearer')
    @transactions_ns.expect(update_model)
    @token_required
    def put(self, transaction_id):
        """Update a transaction"""
        item = Transaction.query.filter_by(id=transaction_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction not found'}, 404
        data = request.json
        if 'date' in data:
            item.date = datetime.fromisoformat(data['date'])
        for field in ['title', 'amount', 'category_id', 'type_id', 'description']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction updated'}, 200

    @transactions_ns.doc(security='Bearer')
    @token_required
    def delete(self, transaction_id):
        """Delete a transaction"""
        item = Transaction.query.filter_by(id=transaction_id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction deleted'}, 200
