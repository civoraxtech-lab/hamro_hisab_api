from flask import g, request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required
from utils.context import get_active_profile
from services.liability_service import LiabilityService

liabilities_ns = Namespace('liabilities', description='Liability operations', path='/api/liabilities')

update_model = liabilities_ns.model('UpdateLiability', {
    'settled_amount': fields.Float(example=400.00),
    'is_verified': fields.Boolean(example=True)
})


@liabilities_ns.route('/')
class LiabilityList(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List liabilities for the active profile"""
        profile = get_active_profile(g.user.id)
        return LiabilityService.get_by_profile(profile.id), 200


@liabilities_ns.route('/<string:liability_id>')
class LiabilityDetail(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self, liability_id):
        """Get a liability by ID"""
        item = LiabilityService.get_by_id(liability_id)
        if not item:
            return {'message': 'Liability not found'}, 404
        return item.to_dict, 200

    @liabilities_ns.doc(security='Bearer')
    @liabilities_ns.expect(update_model)
    @token_required
    def put(self, liability_id):
        """Update settled amount or verification status"""
        item = LiabilityService.update(liability_id, request.json)
        if not item:
            return {'message': 'Liability not found'}, 404
        return {'message': 'Liability updated'}, 200
