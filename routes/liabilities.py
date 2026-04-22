from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, Liability
from utils.decorators import token_required

liabilities_ns = Namespace('liabilities', description='Liability operations', path='/api/liabilities')

create_model = liabilities_ns.model('CreateLiability', {
    'transaction_id': fields.String(required=True, example='uuid-here'),
    'profile_id': fields.String(required=True, example='uuid-here'),
    'settlement_amount': fields.Float(required=True, example=400.00),
    'initial_payer': fields.Boolean(example=False),
    'is_verified': fields.Boolean(example=False)
})

update_model = liabilities_ns.model('UpdateLiability', {
    'settled_amount': fields.Float(example=400.00),
    'is_verified': fields.Boolean(example=True)
})


def serialize(l):
    return {
        'id': str(l.id),
        'transaction_id': str(l.transaction_id) if l.transaction_id else None,
        'profile_id': str(l.profile_id) if l.profile_id else None,
        'settlement_amount': float(l.settlement_amount) if l.settlement_amount else None,
        'settled_amount': float(l.settled_amount) if l.settled_amount else 0.0,
        'initial_payer': l.initial_payer,
        'is_verified': l.is_verified,
        'created_at': str(l.created_at)
    }


@liabilities_ns.route('/')
class LiabilityList(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all liabilities"""
        items = Liability.query.filter_by(deleted_at=None).all()
        return [serialize(l) for l in items], 200

    @liabilities_ns.doc(security='Bearer')
    @liabilities_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a liability"""
        data = request.json
        item = Liability(
            transaction_id=data['transaction_id'],
            profile_id=data['profile_id'],
            settlement_amount=data['settlement_amount'],
            initial_payer=data.get('initial_payer', False),
            is_verified=data.get('is_verified', False)
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Liability created', 'id': str(item.id)}, 201


@liabilities_ns.route('/<string:liability_id>')
class LiabilityDetail(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self, liability_id):
        """Get a liability by ID"""
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return {'message': 'Liability not found'}, 404
        return serialize(item), 200

    @liabilities_ns.doc(security='Bearer')
    @liabilities_ns.expect(update_model)
    @token_required
    def put(self, liability_id):
        """Update a liability (settle)"""
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return {'message': 'Liability not found'}, 404
        data = request.json
        for field in ['settled_amount', 'is_verified']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Liability updated'}, 200

    @liabilities_ns.doc(security='Bearer')
    @token_required
    def delete(self, liability_id):
        """Delete a liability"""
        item = Liability.query.filter_by(id=liability_id, deleted_at=None).first()
        if not item:
            return {'message': 'Liability not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Liability deleted'}, 200
