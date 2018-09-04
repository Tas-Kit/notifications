from werkzeug.exceptions import BadRequest
import json
import onesignal
from uuid import UUID
from mongoengine.errors import ValidationError

from src.constants import ERROR_CODE
from src.models import User
from src import models, onesignal_client


def handle_error(error, error_code):
    print(error)
    bad_request = BadRequest()
    bad_request.data = {
        'detail': error,
        'error_code': error_code
    }
    raise bad_request


def modify_player_id(uid, player_id, register=True):
    player_id = UUID(player_id)
    u = User.objects(uid=uid).modify(upsert=True, new=True, set__uid=uid)
    if register:
        if player_id not in u.player_ids:
            u.update(push__player_ids=player_id)
    else:
        if player_id in u.player_ids:
            u.update(pull__player_ids=player_id)


def parse_params(params):
    try:
        return json.loads(params)
    except Exception as e:
        handle_error(e, ERROR_CODE.JSON_PARSE_ERROR)


def insert_notification(users, notitype, params):
    params = parse_params(params)
    try:
        notification_class = getattr(models, notitype)
        notification = notification_class(**params)
        notification = notification.populate()
        notification = notification.save()
        users.update(push__notifications=notification)
        return notification
    except AttributeError as e:
        handle_error(e, ERROR_CODE.NOTIFICATION_CLASS_ERROR)
    except ValidationError as e:
        handle_error(e, ERROR_CODE.VALIDATION_ERROR)
    except Exception as e:
        handle_error(e, ERROR_CODE.DATABASE_ERROR)


def get_player_ids(users):
    player_ids = []
    for user in users:
        player_ids += user.player_ids
    return [str(player_id) for player_id in player_ids]


def send_notification(users, notification):
    try:
        contents = notification.get_contents()
        new_notification = onesignal.Notification(contents=contents)
        # set target
        new_notification.post_body['include_player_ids'] = get_player_ids(users)

        # send notification, it will return a response
        onesignal_response = onesignal_client.send_notification(new_notification)
        print(onesignal_response.status_code)
        print(onesignal_response.json())

    except onesignal.error.OneSignalError as e:
        handle_error(e, ERROR_CODE.SEND_NOTIFICATION_ERROR)


def push_notification(uid_list, notitype, params):
    users = User.objects(uid__in=uid_list)
    if users:
        notification = insert_notification(users, notitype, params)
        send_notification(users, notification)
