from flask import g, request
from flask_restx import Namespace, Resource, fields
from utils.decorators import token_required, admin_required
from services.category_service import CategoryService

admin_categories_ns = Namespace(
    'admin-categories',
    description='Admin: full category management',
    path='/api/admin/categories',
)

_create = admin_categories_ns.model('AdminCreateCategory', {
    'name': fields.String(required=True, example='Food'),
    'icon': fields.String(example='food-icon'),
    'iconColor': fields.String(example='#FF5733'),
    'is_default': fields.Boolean(example=True),
})

_update = admin_categories_ns.model('AdminUpdateCategory', {
    'name': fields.String(example='Food'),
    'icon': fields.String(example='food-icon'),
    'iconColor': fields.String(example='#FF5733'),
    'is_default': fields.Boolean(example=True),
})


@admin_categories_ns.route('/')
class AdminCategoryList(Resource):
    @admin_categories_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self):
        """List all categories including soft-deleted"""
        return CategoryService.get_all(include_deleted=True), 200

    @admin_categories_ns.doc(security='Bearer')
    @admin_categories_ns.expect(_create)
    @token_required
    @admin_required
    def post(self):
        """Create a system-wide category"""
        item = CategoryService.create(request.json, g.user.id)
        return {'message': 'Category created', 'id': str(item.id)}, 201


@admin_categories_ns.route('/<string:category_id>')
class AdminCategoryDetail(Resource):
    @admin_categories_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def get(self, category_id):
        """Get a category by ID (including soft-deleted)"""
        item = CategoryService.get_by_id(category_id, include_deleted=True)
        if not item:
            return {'message': 'Category not found'}, 404
        return item.to_dict, 200

    @admin_categories_ns.doc(security='Bearer')
    @admin_categories_ns.expect(_update)
    @token_required
    @admin_required
    def put(self, category_id):
        """Update any category"""
        item = CategoryService.update(category_id, request.json)
        if not item:
            return {'message': 'Category not found'}, 404
        return {'message': 'Category updated'}, 200

    @admin_categories_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def delete(self, category_id):
        """Soft-delete a category"""
        item = CategoryService.soft_delete(category_id)
        if not item:
            return {'message': 'Category not found'}, 404
        return {'message': 'Category deleted'}, 200


@admin_categories_ns.route('/<string:category_id>/restore')
class AdminCategoryRestore(Resource):
    @admin_categories_ns.doc(security='Bearer')
    @token_required
    @admin_required
    def post(self, category_id):
        """Restore a soft-deleted category"""
        item = CategoryService.restore(category_id)
        if not item:
            return {'message': 'Category not found or not deleted'}, 404
        return {'message': 'Category restored'}, 200
