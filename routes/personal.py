from flask import g, request
from flask_restx import Namespace, Resource
from utils.decorators import token_required
from controllers.personal.dashboard import DashboardController
from controllers.personal.transactions import TransactionController

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
        try:
            data = request.get_json()
            result = TransactionController.create(g.user, data)
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500
