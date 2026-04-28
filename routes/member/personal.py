from flask import g, request
from flask_restx import Namespace, Resource
from utils.decorators import token_required
from utils.context import get_active_profile
from controllers.personal.dashboard import DashboardController
from services.transaction_service import create_transaction

personal_ns = Namespace('personal', description='Personal finance operations', path='/api/personal')


@personal_ns.route('/')
class PersonalDashboard(Resource):
    @personal_ns.doc(security='Bearer')
    @token_required
    def get(self):
        try:
            data = DashboardController.index(g.user)
            return data, 200
        except Exception as e:
            return {"error": str(e)}, 500


@personal_ns.route('/transactions/create')
class CreateTransaction(Resource):
    @personal_ns.doc(security='Bearer')
    @token_required
    def post(self):
        data = request.get_json()
        profile = get_active_profile(g.user.id)
        try:
            tx = create_transaction(profile, g.user, data)
            return {'message': 'Transaction created', 'id': str(tx.id)}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
