from flask import Flask
from flask_mongoengine import MongoEngine
import redis
import onesignal
from collections import defaultdict

from settings import (
    NAMEREDIS_HOST,
    NAMEREDIS_PORT,
    ONESIGNAL_APP_AUTH_KEY,
    ONESIGNAL_USER_AUTH_KEY,
    ONESIGNAL_APP_ID
)

db = MongoEngine()
nameredis = redis.Redis(
    host=NAMEREDIS_HOST,
    port=NAMEREDIS_PORT)

onesignal_client = onesignal.Client(
    user_auth_key=ONESIGNAL_USER_AUTH_KEY,
    app={
        "app_auth_key": ONESIGNAL_APP_AUTH_KEY,
        "app_id": ONESIGNAL_APP_ID
    })

name_cache = defaultdict(str)


def create_app():
    app = Flask("Notifications")
    # Load common settings
    app.config.from_object('settings')

    # Register blueprints
    from .views import register_blueprints
    register_blueprints(app)

    # Setup Flask-Mongo
    db.init_app(app)

    @app.route('/healthcheck', methods=['GET'])
    def healthcheck():
        return 'HEALTHY'

    return app
