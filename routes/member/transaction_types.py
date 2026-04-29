from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.transaction_type_service import TransactionTypeService

transaction_types_ns = Namespace(
    'transaction-types',
    description='Transaction type lookup',
    path='/api/transaction-types'
)


@transaction_types_ns.route('/')
class TransactionTypeList(Resource):
    @transaction_types_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active transaction types"""
        return TransactionTypeService.get_all(), 200


@transaction_types_ns.route('/<string:type_id>')
class TransactionTypeDetail(Resource):
    @transaction_types_ns.doc(security='Bearer')
    @token_required
    def get(self, type_id):
        """Get a transaction type by ID"""
        item = TransactionTypeService.get_by_id(type_id)
        if not item:
            return {'message': 'Transaction type not found'}, 404
        return {'id': str(item.id), 'name': item.name, 'status': item.status}, 200
