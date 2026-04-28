from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Transaction
from utils.decorators import token_required
from utils.context import get_active_profile
from services.transaction_service import create_transaction

transactions_ns = Namespace('transactions', description='Transaction operations', path='/api/transactions')

create_model = transactions_ns.model('CreateTransaction', {
    'title': fields.String(required=True, example='Dinner split'),
    'amount': fields.Float(required=True, example=1200.00),
    'category_id': fields.String(required=True, example='uuid-here'),
    'group_id': fields.String(example='uuid-here'),
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
        'category_name': t.category.name if t.category else None,
        'category_icon_color': t.category.iconColor if t.category else None,
        'type_id': str(t.type_id) if t.type_id else None,
        'type_name': t.transaction_type.name if t.transaction_type else None,
        'group_id': str(t.group_id) if t.group_id else None,
        'description': t.description,
        'date': str(t.date) if t.date else None,
        'created_at': str(t.created_at)
    }


@transactions_ns.route('/')
class TransactionList(Resource):
    @transactions_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all transactions for the current user"""
        items = Transaction.query.filter_by(
            created_by=g.user.id,
            deleted_at=None
        ).order_by(Transaction.date.desc()).all()
        return [serialize(t) for t in items], 200

    @transactions_ns.doc(security='Bearer')
    @transactions_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a transaction and its initial liability"""
        profile = get_active_profile(g.user.id)
        try:
            item = create_transaction(profile, g.user, request.json)
            return {'message': 'Transaction created', 'id': str(item.id)}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@transactions_ns.route('/<string:transaction_id>')
class TransactionDetail(Resource):
    @transactions_ns.doc(security='Bearer')
    @token_required
    def get(self, transaction_id):
        """Get a transaction by ID"""
        item = Transaction.query.filter_by(id=transaction_id, created_by=g.user.id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction not found'}, 404
        return serialize(item), 200

    @transactions_ns.doc(security='Bearer')
    @transactions_ns.expect(update_model)
    @token_required
    def put(self, transaction_id):
        """Update a transaction"""
        item = Transaction.query.filter_by(id=transaction_id, created_by=g.user.id, deleted_at=None).first()
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
        item = Transaction.query.filter_by(id=transaction_id, created_by=g.user.id, deleted_at=None).first()
        if not item:
            return {'message': 'Transaction not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Transaction deleted'}, 200
