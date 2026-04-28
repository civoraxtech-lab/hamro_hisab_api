from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.subscription_type_service import SubscriptionTypeService

admin_sub_types_ns = Namespace(
    'admin-subscription-types',
    description='Admin: subscription type management',
    path='/api/admin/subscription-types',
)

_create = admin_sub_types_ns.model('AdminCreateSubscriptionType', {
    'name': fields.String(required=True, example='Monthly Basic'),
    'price': fields.Float(required=True, example=499.00),
    'status': fields.String(example='ACTIVE'),
})

_update = admin_sub_types_ns.model('AdminUpdateSubscriptionType', {
    'name': fields.String(example='Monthly Basic'),
    'price': fields.Float(example=499.00),
    'status': fields.String(example='ACTIVE'),
})


@admin_sub_types_ns.route('/')
class AdminSubscriptionTypeList(Resource):
    @admin_sub_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all subscription types"""
        return SubscriptionTypeService.get_all(), 200

    @admin_sub_types_ns.doc(security='Bearer')
    @admin_sub_types_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a subscription type"""
        item = SubscriptionTypeService.create(request.json)
        return {'message': 'Subscription type created', 'id': str(item.id)}, 201


@admin_sub_types_ns.route('/<string:type_id>')
class AdminSubscriptionTypeDetail(Resource):
    @admin_sub_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, type_id):
        """Get a subscription type by ID"""
        item = SubscriptionTypeService.get_by_id(type_id)
        if not item:
            return {'message': 'Subscription type not found'}, 404
        return {'id': str(item.id), 'name': item.name, 'price': float(item.price), 'status': item.status}, 200

    @admin_sub_types_ns.doc(security='Bearer')
    @admin_sub_types_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, type_id):
        """Update a subscription type"""
        item = SubscriptionTypeService.update(type_id, request.json)
        if not item:
            return {'message': 'Subscription type not found'}, 404
        return {'message': 'Subscription type updated'}, 200

    @admin_sub_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, type_id):
        """Soft-delete a subscription type"""
        item = SubscriptionTypeService.soft_delete(type_id)
        if not item:
            return {'message': 'Subscription type not found'}, 404
        return {'message': 'Subscription type deleted'}, 200
