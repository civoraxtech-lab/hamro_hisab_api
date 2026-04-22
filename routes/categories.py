from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Category
from utils.decorators import token_required

categories_ns = Namespace('categories', description='Category operations', path='/api/categories')

create_model = categories_ns.model('CreateCategory', {
    'name': fields.String(required=True, example='Food'),
    'icon': fields.String(example='food-icon'),
    'iconColor': fields.String(example='#FF5733'),
    'is_default': fields.Boolean(example=False)
})

update_model = categories_ns.model('UpdateCategory', {
    'name': fields.String(example='Food'),
    'icon': fields.String(example='food-icon'),
    'iconColor': fields.String(example='#FF5733'),
    'is_default': fields.Boolean(example=False)
})


def serialize(c):
    return {
        'id': str(c.id),
        'name': c.name,
        'icon': c.icon,
        'iconColor': c.iconColor,
        'is_default': c.is_default,
        'created_by': str(c.created_by) if c.created_by else None
    }


@categories_ns.route('/')
class CategoryList(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all categories"""
        items = Category.query.filter_by(deleted_at=None).all()
        return [serialize(c) for c in items], 200

    @categories_ns.doc(security='Bearer')
    @categories_ns.expect(create_model)
    @token_required
    def post(self):
        """Create a category"""
        data = request.json
        item = Category(
            name=data['name'],
            icon=data.get('icon'),
            iconColor=data.get('iconColor'),
            is_default=data.get('is_default', False),
            created_by=g.user.id
        )
        db.session.add(item)
        db.session.commit()
        return {'message': 'Category created', 'id': str(item.id)}, 201


@categories_ns.route('/<string:category_id>')
class CategoryDetail(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self, category_id):
        """Get a category by ID"""
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return {'message': 'Category not found'}, 404
        return serialize(item), 200

    @categories_ns.doc(security='Bearer')
    @categories_ns.expect(update_model)
    @token_required
    def put(self, category_id):
        """Update a category"""
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return {'message': 'Category not found'}, 404
        data = request.json
        for field in ['name', 'icon', 'iconColor', 'is_default']:
            if field in data:
                setattr(item, field, data[field])
        item.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Category updated'}, 200

    @categories_ns.doc(security='Bearer')
    @token_required
    def delete(self, category_id):
        """Delete a category"""
        item = Category.query.filter_by(id=category_id, deleted_at=None).first()
        if not item:
            return {'message': 'Category not found'}, 404
        item.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return {'message': 'Category deleted'}, 200
