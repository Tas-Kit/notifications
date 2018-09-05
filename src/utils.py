from werkzeug.exceptions import BadRequest
import json
from requests.exceptions import HTTPError
from onesignalclient.notification import Notification
from uuid import UUID
from mongoengine.errors import ValidationError

from src.constants import ERROR_CODE
from src.models import User
from src import models, onesignal_client, nameredis, name_cache
from settings import ONESIGNAL_APP_ID


def handle_error(error, error_code):
    print(error)
    bad_request = BadRequest()
    bad_request.data = {
        'detail': str(error),
        'error_code': error_code
    }
    raise bad_request


def get_data_ids(notifications):
    ids = set()
    for notification in notifications:
        for key in notification.params.keys():
            data_id = getattr(notification, key, None)
            ids.add(data_id)
    return list(ids)


def populate_name_cache(notifications):
    ids = get_data_ids(notifications)
    try:
        pipe = nameredis.pipeline()
        for data_id in ids:
            pipe.get(data_id)
        values = pipe.execute()
        for i in range(len(ids)):
            name_cache[ids[i]] = values[i].decode('utf-8')
    except Exception as e:
        handle_error(e, ERROR_CODE.NAMEREDIS_ERROR)


def get_user(uid):
    return User.objects(uid=uid).modify(upsert=True, new=True, set__uid=uid)


def modify_player_id(uid, player_id, register=True):
    player_id = UUID(player_id)
    u = get_user(uid)
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
    player_ids = [str(player_id) for player_id in player_ids]
    print(player_ids)
    return player_ids


def send_notification(users, notification):
    populate_name_cache([notification])
    contents = notification.get_contents()
    new_notification = Notification(
        ONESIGNAL_APP_ID,
        Notification.DEVICES_MODE)
    # set target
    new_notification.include_player_ids = get_player_ids(users)
    new_notification.contents = contents

    try:
        # Sends it!
        result = onesignal_client.create_notification(new_notification)
        print(result)
    except HTTPError as e:
        handle_error(e, ERROR_CODE.SEND_NOTIFICATION_ERROR)


def push_notification(uid_list, notitype, params):
    users = User.objects(uid__in=uid_list)
    if users:
        notification = insert_notification(users, notitype, params)
        send_notification(users, notification)
