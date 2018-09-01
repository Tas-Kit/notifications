from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    # Load common settings
    app.config.from_object('settings')

    # Register blueprints
    from .views import register_blueprints
    register_blueprints(app)

    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup Flask-Migrate
    migrate.init_app(app, db)

    @app.route('/healthcheck', methods=['GET'])
    def healthcheck():
        return 'HEALTHY'

    return app
