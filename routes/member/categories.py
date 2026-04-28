from flask_restx import Namespace, Resource
from utils.decorators import token_required
from services.category_service import CategoryService

categories_ns = Namespace('categories', description='Category lookup', path='/api/categories')


@categories_ns.route('/')
class CategoryList(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self):
        """List all active categories"""
        return CategoryService.get_all(), 200


@categories_ns.route('/<string:category_id>')
class CategoryDetail(Resource):
    @categories_ns.doc(security='Bearer')
    @token_required
    def get(self, category_id):
        """Get a category by ID"""
        item = CategoryService.get_by_id(category_id)
        if not item:
            return {'message': 'Category not found'}, 404
        return item.to_dict, 200
