from flask import g
from flask_restx import Namespace, Resource
from utils.decorators import token_required
from utils.context import get_active_profile
from services.dashboard_service import DashboardService

personal_ns = Namespace('personal', description='Personal finance dashboard', path='/api/personal')


@personal_ns.route('/')
class PersonalDashboard(Resource):
    @personal_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """Summary dashboard for the active profile"""
        profile = get_active_profile(g.user.id)
        data = DashboardService.get_summary(profile)
        return data, 200
