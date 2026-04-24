from datetime import datetime, timezone
from flask import request
from flask_restx import Namespace, Resource, fields
from db import db, SubscriptionType
from utils.decorators import token_required

subscription_types_ns = Namespace('subscription-types', description='Subscription type operations', path='/api/subscription-types')

create_model = subscription_types_ns.model('CreateSubscriptionType', {
    'name': fields.String(required=True, example='Monthly Basic'),
    'price': fields.Float(required=True, example=499.00),
    'status': fields.String(example='ACTIVE')
})

update_model = subscription_types_ns.model('UpdateSubscriptionType', {
    'name': fields.String(example='Monthly Basic'),
    'price': fields.Float(example=499.00),
    'status': fields.String(example='ACTIVE')
})


def serialize(s):
    return {
        'id': str(s.id),
        'name': s.name,
        'price': float(s.price),
        'status': s.status,
        'created_at': str(s.created_at)
    }


@subscription_types_ns.route('/')
class SubscriptionTypeList(Resource):
    @subscription_types_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all subscription types"""
        items = SubscriptionType.query.filter_by(deleted_at=None).all()
        return [serialize(s) for s in items], 200

    @subscription_types_ns.doc(security='Bearer')
    @subscription_types_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a subscription type"""
        data = request.json
        item = SubscriptionType(
            name=data['name'],
            price=data['price'],
            status=data.get('status', 'ACTIVE')
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Subscription type created', 'id': str(item.id)}, 201


@subscription_types_ns.route('/<string:type_id>')
class SubscriptionTypeDetail(Resource):
    @subscription_types_ns.doc(security='Bearer')
    @token_required
    def get(self, type_id):
        """Get a subscription type by ID"""
        item = SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription type not found'}, 404
        return serialize(item), 200

    @subscription_types_ns.doc(security='Bearer')
    @subscription_types_ns.expect(update_model)
    @token_required
    def put(self, type_id):
        """Update a subscription type"""
        item = SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription type not found'}, 404
        data = request.json
        for field in ['name', 'price', 'status']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription type updated'}, 200

    @subscription_types_ns.doc(security='Bearer')
    @token_required
    def delete(self, type_id):
        """Delete a subscription type"""
        item = SubscriptionType.query.filter_by(id=type_id, deleted_at=None).first()
        if not item:
            return {'message': 'Subscription type not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Subscription type deleted'}, 200
