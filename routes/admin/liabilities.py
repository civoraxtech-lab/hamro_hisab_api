from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.liability_service import LiabilityService

admin_liabilities_ns = Namespace(
    'admin-liabilities',
    description='Admin: full liability management',
    path='/api/admin/liabilities',
)

_create = admin_liabilities_ns.model('AdminCreateLiability', {
    'transaction_id': fields.String(required=True, example='uuid-here'),
    'profile_id': fields.String(required=True, example='uuid-here'),
    'settlement_amount': fields.Float(required=True, example=400.00),
    'initial_payer': fields.Boolean(example=False),
    'is_verified': fields.Boolean(example=False),
})

_update = admin_liabilities_ns.model('AdminUpdateLiability', {
    'settled_amount': fields.Float(example=400.00),
    'is_verified': fields.Boolean(example=True),
})


@admin_liabilities_ns.route('/')
class AdminLiabilityList(Resource):
    @admin_liabilities_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all liabilities"""
        return LiabilityService.get_all(), 200

    @admin_liabilities_ns.doc(security='Bearer')
    @admin_liabilities_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a liability manually"""
        item = LiabilityService.create(request.json)
        return {'message': 'Liability created', 'id': str(item.id)}, 201


@admin_liabilities_ns.route('/<string:liability_id>')
class AdminLiabilityDetail(Resource):
    @admin_liabilities_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, liability_id):
        """Get any liability by ID"""
        item = LiabilityService.get_by_id(liability_id)
        if not item:
            return {'message': 'Liability not found'}, 404
        return item.to_dict, 200

    @admin_liabilities_ns.doc(security='Bearer')
    @admin_liabilities_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, liability_id):
        """Update a liability"""
        item = LiabilityService.update(liability_id, request.json)
        if not item:
            return {'message': 'Liability not found'}, 404
        return {'message': 'Liability updated'}, 200

    @admin_liabilities_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, liability_id):
        """Soft-delete a liability"""
        item = LiabilityService.soft_delete(liability_id)
        if not item:
            return {'message': 'Liability not found'}, 404
        return {'message': 'Liability deleted'}, 200
