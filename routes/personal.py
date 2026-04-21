from flask import Blueprint,g,jsonify,request
from utils.decorators import token_required
from controllers.personal.dashboard import DashboardController
from controllers.personal.transactions import TransactionController

personal_bp = Blueprint('personal', __name__)

# This runs the token check for EVERY route in this blueprint automatically
@personal_bp.before_request
@token_required
def before_request(current_user):
    g.user = current_user

@personal_bp.route('/', methods=['GET'])
def index():
    try:
        data = DashboardController.index(g.user)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@personal_bp.route('/transactions/create', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()
        result = TransactionController.create(g.user, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500