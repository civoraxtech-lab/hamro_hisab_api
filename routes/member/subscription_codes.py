from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.subscription_code_service import SubscriptionCodeService

subscription_codes_ns = Namespace(
    'subscription-codes',
    description='Subscription code lookup',
    path='/api/subscription-codes'
)


@subscription_codes_ns.route('/')
class SubscriptionCodeList(Resource):
    @subscription_codes_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active subscription codes"""
        return SubscriptionCodeService.get_all(), 200


@subscription_codes_ns.route('/<string:code_id>')
class SubscriptionCodeDetail(Resource):
    @subscription_codes_ns.doc(security='Bearer')
    @token_required
    def get(self, code_id):
        """Get a subscription code by ID"""
        item = SubscriptionCodeService.get_by_id(code_id)
        if not item:
            return {'message': 'Subscription code not found'}, 404
        return {
            'id': str(item.id),
            'code': item.code,
            'discount': float(item.discount) if item.discount else None,
            'is_percent': item.is_percent,
            'status': item.status,
        }, 200
