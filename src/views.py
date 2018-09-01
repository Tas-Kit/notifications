# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Blueprint


main_blueprint = Blueprint('main', __name__)


def register_blueprints(app):
    app.register_blueprint(main_blueprint, url_prefix='/api/v1/notifications')


@main_blueprint.route('/')
def hello():
    return 'Hello World'
