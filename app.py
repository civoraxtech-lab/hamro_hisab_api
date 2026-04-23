import os
from flask import Flask
from dotenv import load_dotenv
from db.database import db
from core.extensions import migrate, api
from core.commands import register_commands
from routes import (
    auth_ns, users_ns, profiles_ns, categories_ns,
    group_ns, transactions_ns, liabilities_ns,
    subscriptions_ns, subscription_types_ns, subscription_codes_ns,
    roles_ns, personal_ns
)

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app) # Initialize API with the app

    # Register Namespaces
    namespaces = [
        auth_ns, users_ns, profiles_ns, categories_ns,
        group_ns, transactions_ns, liabilities_ns,
        subscriptions_ns, subscription_types_ns, subscription_codes_ns,
        roles_ns, personal_ns
    ]
    for ns in namespaces:
        api.add_namespace(ns)

    # Register CLI Commands
    register_commands(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)