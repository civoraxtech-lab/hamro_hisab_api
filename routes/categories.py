from datetime import datetime, timezone
from flask import g, request
from flask_restx import Namespace, Resource, fields
from db import db, Category
from utils.decorators import token_required
from controllers.member.category import CategoryController


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


@categories_ns.route('/')
class CategoryList(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self):
        items = CategoryController.index()
        return items, 200

    @categories_ns.doc(security='Bearer')
    @categories_ns.expect(create_model)
    @token_required
    def post(self):
        item = CategoryController.create(request.json, g.user.id)
        return {'message': 'Category created', 'id': str(item.id)}, 201
       

@categories_ns.route('/<string:category_id>')
class CategoryDetail(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self, category_id):
        item = CategoryController.show(category_id)
        if not item:
            return {'message': 'Category not found'}, 404
        
        return item,200


    @categories_ns.doc(security='Bearer')
    @categories_ns.expect(update_model)
    @token_required
    def put(self, category_id):
        updated_item = CategoryController.update(category_id, request.json)
        if not updated_item:
            return {'message': 'Category not found'}, 404
            
        return {'message': 'Category updated'}, 200
    

    @categories_ns.doc(security='Bearer')
    @token_required
    def delete(self, category_id):
        item = CategoryController.delete(category_id)
        if not item:
            return {'message': 'Category not found'}, 404
            
        return {'message': 'Category deleted'}, 200
