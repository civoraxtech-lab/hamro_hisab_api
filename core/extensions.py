from flask_migrate import Migrate
from flask_restx import Api

migrate = Migrate()

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Paste your token as: **Bearer &lt;your_token&gt;**"
    }
}

api = Api(
    doc="/docs",
    title="Hamro Hisab API",
    version="1.0",
    description="Personal and group expense tracker",
    authorizations=authorizations,
    security='Bearer'
)