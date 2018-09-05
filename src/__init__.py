from flask import Flask
from flask_mongoengine import MongoEngine
import redis
from collections import defaultdict
from onesignalclient.app_client import OneSignalAppClient

from settings import (
    NAMEREDIS_HOST,
    NAMEREDIS_PORT,
    ONESIGNAL_USER_AUTH_KEY,
    ONESIGNAL_APP_ID
)

db = MongoEngine()
nameredis = redis.Redis(
    host=NAMEREDIS_HOST,
    port=NAMEREDIS_PORT)

onesignal_client = OneSignalAppClient(
    app_id=ONESIGNAL_APP_ID,
    app_api_key=ONESIGNAL_USER_AUTH_KEY)

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
