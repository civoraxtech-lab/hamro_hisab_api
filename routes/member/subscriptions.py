from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Subscription
from utils.decorators import token_required

subscriptions_ns = Namespace('subscriptions', description='Subscription operations', path='/api/subscriptions')

create_model = subscriptions_ns.model('CreateSubscription', {
    'user_id': fields.String(required=True, example='uuid-here'),
    'type_id': fields.String(required=True, example='uuid-here'),
    'expiry': fields.String(required=True, example='2026-12-31T00:00:00'),
    'total_amount': fields.Float(required=True, example=4999.00),
    'paid_amount': fields.Float(required=True, example=4999.00),
    'discount': fields.Float(example=0.00),
    'is_percent': fields.Boolean(example=False)
})

update_model = subscriptions_ns.model('UpdateSubscription', {
    'expiry': fields.String(example='2026-12-31T00:00:00'),
    'total_amount': fields.Float(example=4999.00),
    'paid_amount': fields.Float(example=4999.00),
    'discount': fields.Float(example=0.00),
    'is_percent': fields.Boolean(example=False)
})


def serialize(s):
    return {
        'id': str(s.id),
        'user_id': str(s.user_id),
        'type_id': str(s.type_id),
        'expiry': str(s.expiry) if s.expiry else None,
        'total_amount': float(s.total_amount) if s.total_amount else None,
        'paid_amount': float(s.paid_amount) if s.paid_amount else None,
        'discount': float(s.discount) if s.discount else None,
        'is_percent': s.is_percent,
        'created_at': str(s.created_at)
    }


@subscriptions_ns.route('/')
class SubscriptionList(Resource):
    @subscriptions_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List current user's subscriptions"""
        items = Subscription.query.filter_by(user_id=g.user.id, deleted_at=None).all()
        return [serialize(s) for s in items], 200

    @subscriptions_ns.doc(security='Bearer')
    @subscriptions_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a subscription"""
        data = request.json
        item = Subscription(
            user_id=data['user_id'],
            type_id=data['type_id'],
            expiry=datetime.fromisoformat(data['expiry']),
            total_amount=data['total_amount'],
            paid_amount=data['paid_amount'],
            discount=data.get('discount'),
            is_percent=data.get('is_percent', False)
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Subscription created', 'id': str(item.id)}, 201


@subscriptions_ns.route('/<string:subscription_id>')
class SubscriptionDetail(Resource):
    @subscriptions_ns.doc(security='Bearer')
    @token_required
    def get(self, subscription_id):
        """Get a subscription by ID"""
        item = Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription not found'}, 404
        return serialize(item), 200

    @subscriptions_ns.doc(security='Bearer')
    @subscriptions_ns.expect(update_model)
    @token_required
    def put(self, subscription_id):
        """Update a subscription"""
        item = Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription not found'}, 404
        data = request.json
        if 'expiry' in data:
            item.expiry = datetime.fromisoformat(data['expiry'])
        for field in ['total_amount', 'paid_amount', 'discount', 'is_percent']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription updated'}, 200

    @subscriptions_ns.doc(security='Bearer')
    @token_required
    def delete(self, subscription_id):
        """Delete a subscription"""
        item = Subscription.query.filter_by(id=subscription_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription deleted'}, 200
