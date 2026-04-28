from flask import request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.transaction_type_service import TransactionTypeService

admin_tx_types_ns = Namespace(
    'admin-transaction-types',
    description='Admin: transaction type management (INCOME / EXPENSE)',
    path='/api/admin/transaction-types',
)

_create = admin_tx_types_ns.model('AdminCreateTransactionType', {
    'name': fields.String(required=True, example='EXPENSE'),
    'status': fields.String(example='ACTIVE'),
})

_update = admin_tx_types_ns.model('AdminUpdateTransactionType', {
    'name': fields.String(example='EXPENSE'),
    'status': fields.String(example='ACTIVE'),
})


@admin_tx_types_ns.route('/')
class AdminTransactionTypeList(Resource):
    @admin_tx_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all transaction types"""
        return TransactionTypeService.get_all(), 200

    @admin_tx_types_ns.doc(security='Bearer')
    @admin_tx_types_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a transaction type"""
        item = TransactionTypeService.create(request.json)
        return {'message': 'Transaction type created', 'id': str(item.id)}, 201


@admin_tx_types_ns.route('/<string:type_id>')
class AdminTransactionTypeDetail(Resource):
    @admin_tx_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, type_id):
        """Get a transaction type by ID"""
        item = TransactionTypeService.get_by_id(type_id)
        if not item:
            return {'message': 'Transaction type not found'}, 404
        return {'id': str(item.id), 'name': item.name, 'status': item.status}, 200

    @admin_tx_types_ns.doc(security='Bearer')
    @admin_tx_types_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, type_id):
        """Update a transaction type"""
        item = TransactionTypeService.update(type_id, request.json)
        if not item:
            return {'message': 'Transaction type not found'}, 404
        return {'message': 'Transaction type updated'}, 200

    @admin_tx_types_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, type_id):
        """Soft-delete a transaction type"""
        item = TransactionTypeService.soft_delete(type_id)
        if not item:
            return {'message': 'Transaction type not found'}, 404
        return {'message': 'Transaction type deleted'}, 200
