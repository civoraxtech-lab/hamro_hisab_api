from flask import Flask
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_restx import Api
from db import db, User, Group, Transaction, seed_data
from routes import (
    auth_ns, users_ns, profiles_ns, categories_ns,
    group_ns, transactions_ns, liabilities_ns,
    subscriptions_ns, subscription_types_ns, subscription_codes_ns,
    roles_ns, personal_ns
)
from utils.decorators import generateToken

load_dotenv()

def create_app():
    app = Flask(__name__)

    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Paste your token as: **Bearer &lt;your_token&gt;**"
        }
    }

    api = Api(
        app,
        doc="/docs",
        title="Hamro Hisab API",
        version="1.0",
        description="Personal and group expense tracker",
        authorizations=authorizations,
        security='Bearer'
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api.add_namespace(auth_ns)
    api.add_namespace(users_ns)
    api.add_namespace(profiles_ns)
    api.add_namespace(categories_ns)
    api.add_namespace(group_ns)
    api.add_namespace(transactions_ns)
    api.add_namespace(liabilities_ns)
    api.add_namespace(subscriptions_ns)
    api.add_namespace(subscription_types_ns)
    api.add_namespace(subscription_codes_ns)
    api.add_namespace(roles_ns)
    api.add_namespace(personal_ns)

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.cli.command("db-refresh")
    def db_refresh():
        db.drop_all()
        print("All tables dropped.")
        db.create_all()
        print("All tables recreated.")

    @app.cli.command("db-seed")
    def db_seed():
        seed_data()
        print("Database successfully seeded with Hamro Hisab test data!")

    @app.cli.command("get-token")
    def get_token():
        user = User.query.first()
        token = generateToken(user)
        print(f"\nUser:  {user.email}")
        print(f"Token: Bearer {token}\n")
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
