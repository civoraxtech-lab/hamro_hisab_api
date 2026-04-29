from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.subscription_type_service import SubscriptionTypeService

subscription_types_ns = Namespace(
    'subscription-types',
    description='Subscription type lookup',
    path='/api/subscription-types'
)


@subscription_types_ns.route('/')
class SubscriptionTypeList(Resource):
    @subscription_types_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active subscription types"""
        return SubscriptionTypeService.get_all(), 200


@subscription_types_ns.route('/<string:type_id>')
class SubscriptionTypeDetail(Resource):
    @subscription_types_ns.doc(security='Bearer')
    @token_required
    def get(self, type_id):
        """Get a subscription type by ID"""
        item = SubscriptionTypeService.get_by_id(type_id)
        if not item:
            return {'message': 'Subscription type not found'}, 404
        return {'id': str(item.id), 'name': item.name, 'price': float(item.price), 'status': item.status}, 200
