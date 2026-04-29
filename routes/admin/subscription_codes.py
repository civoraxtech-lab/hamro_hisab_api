from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.subscription_code_service import SubscriptionCodeService

admin_sub_codes_ns = Namespace(
    'admin-subscription-codes',
    description='Admin: subscription promo code management',
    path='/api/admin/subscription-codes',
)

_create = admin_sub_codes_ns.model('AdminCreateSubscriptionCode', {
    'code': fields.String(required=True, example='SAVE20'),
    'discount': fields.Float(example=20.00),
    'is_percent': fields.Boolean(example=True),
    'status': fields.String(example='ACTIVE'),
})

_update = admin_sub_codes_ns.model('AdminUpdateSubscriptionCode', {
    'code': fields.String(example='SAVE20'),
    'discount': fields.Float(example=20.00),
    'is_percent': fields.Boolean(example=True),
    'status': fields.String(example='ACTIVE'),
})


@admin_sub_codes_ns.route('/')
class AdminSubscriptionCodeList(Resource):
    @admin_sub_codes_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all promo codes"""
        return SubscriptionCodeService.get_all(), 200

    @admin_sub_codes_ns.doc(security='Bearer')
    @admin_sub_codes_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a promo code"""
        item = SubscriptionCodeService.create(request.json)
        return {'message': 'Subscription code created', 'id': str(item.id)}, 201


@admin_sub_codes_ns.route('/<string:code_id>')
class AdminSubscriptionCodeDetail(Resource):
    @admin_sub_codes_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, code_id):
        """Get a promo code by ID"""
        item = SubscriptionCodeService.get_by_id(code_id)
        if not item:
            return {'message': 'Subscription code not found'}, 404
        return {'id': str(item.id), 'code': item.code, 'discount': float(item.discount or 0), 'is_percent': item.is_percent, 'status': item.status}, 200

    @admin_sub_codes_ns.doc(security='Bearer')
    @admin_sub_codes_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, code_id):
        """Update a promo code"""
        item = SubscriptionCodeService.update(code_id, request.json)
        if not item:
            return {'message': 'Subscription code not found'}, 404
        return {'message': 'Subscription code updated'}, 200

    @admin_sub_codes_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, code_id):
        """Soft-delete a promo code"""
        item = SubscriptionCodeService.soft_delete(code_id)
        if not item:
            return {'message': 'Subscription code not found'}, 404
        return {'message': 'Subscription code deleted'}, 200
