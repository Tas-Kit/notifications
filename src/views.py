# __init__.py is a special Python file that allows a directory to become
# a Python package so it can be accessed using the 'import' statement.

from flask import Blueprint
from flask_restplus import Api, Resource, fields, reqparse
from src import utils

main_blueprint = Blueprint('main', __name__)


def register_blueprints(app):
    app.register_blueprint(main_blueprint, url_prefix='/api/v1/notifications')


api = Api(main_blueprint, version='1.0', title='Notifications API',
          description='Notifications API')

notification_model = api.model('Notification', {
    'notitype': fields.String,

})

internal_ns = api.namespace('internal', description='Internal otifications operations.')
user_ns = api.namespace('user', description='For user to query his notifications.')

# Basic parser for parsing uid in cookie section
internal_parser = reqparse.RequestParser()
internal_parser.add_argument('uid_list', type=str, location='form', action='split')
internal_parser.add_argument('params', type=str, location='form')
internal_parser.add_argument('notitype', type=str, location='form')

user_parser = reqparse.RequestParser()
user_parser.add_argument('uid', type=str, location='cookies')
user_parser.add_argument('player_id', type=str, location='form')

uid_parser = reqparse.RequestParser()
uid_parser.add_argument('uid', type=str, location='cookies')


@internal_ns.route('/')
class SendNotificationView(Resource):

    @internal_ns.doc('Send Notifications', params={
        'uid_list': 'uid seperated by , ',
        'notitype': 'type of notification see in \
        https://github.com/Tas-Kit/notifications/blob/master/src/models/notification.py',
        'params': 'json dictionary of the notification params. All params \
        (keys in the dictionary) required'
    }, parser=internal_parser)
    def post(self):
        """
        Send Notifications.
        Send notifications to list of users.
        Notifications will construct the notification instances using the notitype.
        The all params in the notification are required.
        """
        args = internal_parser.parse_args()
        uid_list = args['uid_list']
        notitype = args['notitype']
        params = args['params']
        utils.push_notification(uid_list, notitype, params)
        return 'SUCCESS'


@user_ns.route('/')
class UserNotificationView(Resource):

    @internal_ns.doc('Get all notifications', parser=uid_parser)
    def get(self):
        """
        Get all notifications for current user.
        """
        args = uid_parser.parse_args()
        uid = args['uid']
        user = utils.get_user(uid)
        return {
            'notifications': user.serialize_notifications()
        }

    @internal_ns.doc('Register Device', parser=user_parser)
    def post(self):
        """
        Register the device for current user.
        """
        args = user_parser.parse_args()
        uid = args['uid']
        player_id = args['player_id']
        utils.modify_player_id(uid, player_id, register=True)
        return 'SUCCESS'

    @internal_ns.doc('Remove Device', parser=user_parser)
    def delete(self):
        """
        Unregister a device for current user.
        """
        args = user_parser.parse_args()
        uid = args['uid']
        player_id = args['player_id']
        utils.modify_player_id(uid, player_id, register=False)
        return 'SUCCESS'
