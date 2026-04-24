import click
from db.database import db
from db.models import User, Profile # Adjust import path
from db.seeder import seed_data
from utils.decorators import generateToken

def register_commands(app):
    @app.cli.command("db-refresh")
    def db_refresh():
        db.drop_all()
        db.create_all()
        print("All tables dropped and recreated.")

    @app.cli.command("db-seed")
    def db_seed():
        seed_data()
        print("Database successfully seeded with Hamro Hisab test data!")

    @app.cli.command("get-token")
    def get_token():
        user = User.query.first()
        profile  = Profile.query.filter_by(user_id = user.id).first()
        if user:
            token = generateToken(user)
            print(f"\nUser:  {user.email}")
            print(f"Token: Bearer {token}\n")
            print(f"Profile: {profile.id}\n")
    