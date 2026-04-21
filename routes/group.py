from flask import Blueprint
from utils.decorators import token_required

group_bp = Blueprint('group', __name__)

# This runs the token check for EVERY route in this blueprint automatically
@group_bp.before_request
@token_required
def before_request(current_user):
    # You can store the user in Flask's 'g' object to use in routes
    from flask import g
    g.user = current_user

