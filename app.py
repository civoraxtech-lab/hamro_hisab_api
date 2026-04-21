from flask import Flask
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from db import db, User, Group, Transaction, seed_data 
from routes.auth import auth_bp

# Load the .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # 1. Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Inside your create_app() function:
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # 2. Initialize Plugins
    db.init_app(app)
    migrate = Migrate(app, db)


    @app.cli.command("db-refresh")
    def db_refresh():
        db.drop_all()
        print("🗑️ All tables dropped.")
        db.create_all()
        print("🏗️ All tables recreated.")

    
    @app.cli.command("db-seed")
    def db_seed():
        seed_data()
        print("Database successfully seeded with Hamro Hisab test data!")

    # 4. A simple health-check route
    @app.route('/')
    def index():
        return {"message": "Hamro Hisab API is running", "status": "success"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)