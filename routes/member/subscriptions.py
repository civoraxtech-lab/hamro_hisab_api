from flask import g
from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.subscription_service import SubscriptionService

subscriptions_ns = Namespace('subscriptions', description='Subscription lookup', path='/api/subscriptions')


@subscriptions_ns.route('/')
class SubscriptionList(Resource):
    @subscriptions_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List current user's subscriptions"""
        return SubscriptionService.get_by_user(g.user.id), 200


@subscriptions_ns.route('/<string:subscription_id>')
class SubscriptionDetail(Resource):
    @subscriptions_ns.doc(security='Bearer')
    @token_required
    def get(self, subscription_id):
        """Get a subscription by ID"""
        item = SubscriptionService.get_by_id(subscription_id)
        if not item:
            return {'message': 'Subscription not found'}, 404
        from services.subscription_service import _serialize
        return _serialize(item), 200
