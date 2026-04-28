from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.subscription_service import SubscriptionService

admin_subscriptions_ns = Namespace(
    'admin-subscriptions',
    description='Admin: full subscription management',
    path='/api/admin/subscriptions',
)

_create = admin_subscriptions_ns.model('AdminCreateSubscription', {
    'user_id': fields.String(required=True, example='uuid-here'),
    'type_id': fields.String(required=True, example='uuid-here'),
    'expiry': fields.String(required=True, example='2026-12-31T00:00:00'),
    'total_amount': fields.Float(required=True, example=4999.00),
    'paid_amount': fields.Float(required=True, example=4999.00),
    'discount': fields.Float(example=0.00),
    'is_percent': fields.Boolean(example=False),
})

_update = admin_subscriptions_ns.model('AdminUpdateSubscription', {
    'expiry': fields.String(example='2026-12-31T00:00:00'),
    'total_amount': fields.Float(example=4999.00),
    'paid_amount': fields.Float(example=4999.00),
    'discount': fields.Float(example=0.00),
    'is_percent': fields.Boolean(example=False),
})


@admin_subscriptions_ns.route('/')
class AdminSubscriptionList(Resource):
    @admin_subscriptions_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all subscriptions"""
        return SubscriptionService.get_all(), 200

    @admin_subscriptions_ns.doc(security='Bearer')
    @admin_subscriptions_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a subscription for a user"""
        item = SubscriptionService.create(request.json)
        return {'message': 'Subscription created', 'id': str(item.id)}, 201


@admin_subscriptions_ns.route('/<string:subscription_id>')
class AdminSubscriptionDetail(Resource):
    @admin_subscriptions_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, subscription_id):
        """Get any subscription by ID"""
        item = SubscriptionService.get_by_id(subscription_id)
        if not item:
            return {'message': 'Subscription not found'}, 404
        from services.subscription_service import _serialize
        return _serialize(item), 200

    @admin_subscriptions_ns.doc(security='Bearer')
    @admin_subscriptions_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, subscription_id):
        """Update a subscription"""
        item = SubscriptionService.update(subscription_id, request.json)
        if not item:
            return {'message': 'Subscription not found'}, 404
        return {'message': 'Subscription updated'}, 200

    @admin_subscriptions_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, subscription_id):
        """Soft-delete a subscription"""
        item = SubscriptionService.soft_delete(subscription_id)
        if not item:
            return {'message': 'Subscription not found'}, 404
        return {'message': 'Subscription deleted'}, 200
