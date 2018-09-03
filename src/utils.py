from werkzeug.exceptions import BadRequest
import json
import onesignal

from src.constants import ERROR_CODE
from src.models import User
from src import models, onesignal_client


def register_player_id(uid, player_id):
    u = User.objects(uid=uid).modify(upsert=True, new=True, set__uid=uid)
    if player_id not in u.player_ids:
        u.update(push__player_ids=player_id)


def parse_params(params):
    try:
        return json.loads(params)
    except Exception as e:
        print(e)
        bad_request = BadRequest('Unable to parse json')
        bad_request.data = {
            'detail': e,
            'error_code': ERROR_CODE.JSON_PARSE_ERROR
        }
        raise bad_request


def insert_notification(users, notitype, params):
    params = parse_params(params)
    try:
        notification = getattr(models, notitype)(**params).save()
        users.update(push__notifications=notification)
        return notification
    except Exception as e:
        print(e)
        bad_request = BadRequest('Unable to insert notification')
        bad_request.data = {
            'detail': e,
            'error_code': ERROR_CODE.DATABASE_ERROR
        }
        raise bad_request


def send_notification(users, notification):

    try:
        new_notification = onesignal.Notification(contents=notification.get_contents())

        # set target Segments
        player_ids = []
        for user in users:
            player_ids += user.player_ids
        new_notification.post_body['include_player_ids'] = player_ids

        # send notification, it will return a response
        onesignal_response = onesignal_client.send_notification(new_notification)
        print(onesignal_response.status_code)
        print(onesignal_response.json())

    except onesignal.OneSignalError as e:
        print(e)
        bad_request = BadRequest('Unable to send notification')
        bad_request.data = {
            'detail': e,
            'error_code': ERROR_CODE.SEND_NOTIFICATION_ERROR
        }
        raise bad_request


def push_notification(uid_list, notitype, params):
    users = User.objects(uid__in=uid_list)
    if users:
        notification = insert_notification(users, notitype, params)
        send_notification(users, notification)
