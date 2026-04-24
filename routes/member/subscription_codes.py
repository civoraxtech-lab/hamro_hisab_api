from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, SubscriptionCode
from utils.decorators import token_required

subscription_codes_ns = Namespace('subscription-codes', description='Subscription code operations', path='/api/subscription-codes')

create_model = subscription_codes_ns.model('CreateSubscriptionCode', {
    'code': fields.String(required=True, example='SAVE20'),
    'discount': fields.Float(example=20.00),
    'is_percent': fields.Boolean(example=True),
    'status': fields.String(example='ACTIVE')
})

update_model = subscription_codes_ns.model('UpdateSubscriptionCode', {
    'code': fields.String(example='SAVE20'),
    'discount': fields.Float(example=20.00),
    'is_percent': fields.Boolean(example=True),
    'status': fields.String(example='ACTIVE')
})


def serialize(s):
    return {
        'id': str(s.id),
        'code': s.code,
        'discount': float(s.discount) if s.discount else None,
        'is_percent': s.is_percent,
        'status': s.status,
        'created_at': str(s.created_at)
    }


@subscription_codes_ns.route('/')
class SubscriptionCodeList(Resource):
    @subscription_codes_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all subscription codes"""
        items = SubscriptionCode.query.filter_by(deleted_at=None).all()
        return [serialize(s) for s in items], 200

    @subscription_codes_ns.doc(security='Bearer')
    @subscription_codes_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a subscription code"""
        data = request.json
        item = SubscriptionCode(
            code=data['code'],
            discount=data.get('discount'),
            is_percent=data.get('is_percent', False),
            status=data.get('status', 'ACTIVE')
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Subscription code created', 'id': str(item.id)}, 201


@subscription_codes_ns.route('/<string:code_id>')
class SubscriptionCodeDetail(Resource):
    @subscription_codes_ns.doc(security='Bearer')
    @token_required
    def get(self, code_id):
        """Get a subscription code by ID"""
        item = SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription code not found'}, 404
        return serialize(item), 200

    @subscription_codes_ns.doc(security='Bearer')
    @subscription_codes_ns.expect(update_model)
    @token_required
    def put(self, code_id):
        """Update a subscription code"""
        item = SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription code not found'}, 404
        data = request.json
        for field in ['code', 'discount', 'is_percent', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription code updated'}, 200

    @subscription_codes_ns.doc(security='Bearer')
    @token_required
    def delete(self, code_id):
        """Delete a subscription code"""
        item = SubscriptionCode.query.filter_by(id=code_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription code not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription code deleted'}, 200
