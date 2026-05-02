import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from db.database import db
from core.extensions import migrate, api, cors
from core.commands import register_commands
from routes import (
    # member
    auth_ns, users_ns, profiles_ns, categories_ns,
    group_ns, transaction_types_ns, liabilities_ns,
    subscriptions_ns, subscription_types_ns, subscription_codes_ns, roles_ns,
    invitations_ns,
    # personal
    personal_ns, transactions_ns, settings_ns,
    # admin
    admin_categories_ns, admin_groups_ns, admin_roles_ns,
    admin_liabilities_ns, admin_subscriptions_ns,
    admin_sub_types_ns, admin_sub_codes_ns,
    admin_tx_types_ns, admin_users_ns,
)

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB upload limit
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    api.init_app(app)

    namespaces = [
        # member
        auth_ns, users_ns, profiles_ns, categories_ns,
        group_ns, transaction_types_ns, liabilities_ns,
        subscriptions_ns, subscription_types_ns, subscription_codes_ns, roles_ns,
        invitations_ns,
        # personal
        personal_ns, transactions_ns, settings_ns,
        # admin
        admin_categories_ns, admin_groups_ns, admin_roles_ns,
        admin_liabilities_ns, admin_subscriptions_ns,
        admin_sub_types_ns, admin_sub_codes_ns,
        admin_tx_types_ns, admin_users_ns,
    ]
    for ns in namespaces:
        api.add_namespace(ns)

    register_commands(app)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
