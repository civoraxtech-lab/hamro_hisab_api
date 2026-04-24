from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, Liability
from utils.decorators import token_required
from controllers.member.liabilities import LiabilityController

liabilities_ns = Namespace('liabilities', description='Liability operations', path='/api/liabilities')

create_model = liabilities_ns.model('CreateLiability', {
    'transaction_id': fields.String(required=True, example='uuid-here'),
    'profile_id': fields.String(required=True, example='uuid-here'),
    'settlement_amount': fields.Float(required=True, example=400.00),
    'initial_payer': fields.Boolean(example=False),
    'is_verified': fields.Boolean(example=False)
})

update_model = liabilities_ns.model('UpdateLiability', {
    'settled_amount': fields.Float(example=400.00),
    'is_verified': fields.Boolean(example=True)
})


@liabilities_ns.route('/')
class LiabilityList(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all liabilities"""
        items = LiabilityController.index()
        return items, 200

    @liabilities_ns.doc(security='Bearer')
    @liabilities_ns.expect(create_model)
    @token_required
    def post(self):
        item = LiabilityController.create(request.json)
        return {'message': 'Liability created', 'id': str(item.id)}, 201

@liabilities_ns.route('/<string:liability_id>')
class LiabilityDetail(Resource):
    @liabilities_ns.doc(security='Bearer')
    @token_required
    def get(self, liability_id):
        item = LiabilityController.show(liability_id)
        if not item:
            return {'message': 'Liability not found'}, 404
        
        return item,200

    @liabilities_ns.doc(security='Bearer')
    @liabilities_ns.expect(update_model)
    @token_required
    def put(self, liability_id):
        updated_item = LiabilityController.update(liability_id, request.json)
        if not updated_item:
            return {'message': 'Liability not found'}, 404
            
        return {'message': 'Liability updated'}, 200


    @liabilities_ns.doc(security='Bearer')
    @token_required
    def delete(self, liability_id):
        item = LiabilityController.delete(liability_id)
        if not item:
            return {'message': 'Liability not found'}, 404
            
        return {'message': 'Liability deleted'}, 200
