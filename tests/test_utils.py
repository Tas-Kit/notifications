import pytest
import json
from src import utils
from src.models import User
from uuid import uuid4
from mongoengine.errors import DoesNotExist
from werkzeug.exceptions import BadRequest
from mock import patch, MagicMock
from onesignal.error import OneSignalError


@patch('src.utils.send_notification')
@patch('src.utils.insert_notification', return_value=MagicMock())
@patch('src.models.User.objects', return_value=MagicMock())
def test_push_notification(mock_user, mock_insert_notification, mock_send_notification):
    uid_list = MagicMock()
    notitype = MagicMock()
    params = MagicMock()
    utils.push_notification(uid_list, notitype, params)
    mock_user.called_once_with(uid__in=uid_list)
    mock_insert_notification.called_once_with(mock_user.return_value, notitype, params)
    mock_send_notification.called_once_with(mock_user.return_value, mock_insert_notification.return_value)


@patch('onesignal.Notification')
@patch('src.onesignal_client.send_notification')
def test_send_notification(mock_send_notification, mock_notification):
    mock_notification.return_value = MagicMock()
    users = MagicMock()
    contents = MagicMock()
    notification = MagicMock()
    notification.get_contents.return_value = contents
    utils.send_notification(users, notification)
    mock_notification.called_once_with(contents)
    mock_send_notification.called_once()

    mock_send_notification.side_effect = OneSignalError()
    with pytest.raises(BadRequest):
        utils.send_notification(users, notification)


def test_get_player_ids():
    u1 = MagicMock(spec=User)
    u2 = MagicMock(spec=User)
    player_ids = [uuid4() for _ in range(4)]
    u1.player_ids = player_ids[:2]
    u2.player_ids = player_ids[2:]
    player_ids_str = [str(player_id) for player_id in player_ids]
    assert player_ids_str == utils.get_player_ids([u1, u2])


def populate_side_effect(self):
    return self


@patch('src.models.GenericNotification.populate', autospec=True, side_effect=populate_side_effect)
@patch('src.utils.parse_params', return_value={
    'inviter_id': 'inviter',
    'task_id': 'task'
})
def test_insert_notification(mock_parse_params, mock_populate):
    uid1 = str(uuid4())
    uid2 = str(uuid4())
    users = [User(uid=uid1).save(), User(uid=uid2).save()]
    users = User.objects(uid__in=[uid1, uid2])
    notitype = 'InvitationNotification'
    params = MagicMock()
    notification = utils.insert_notification(users, notitype, params)
    u1 = User.objects.get(uid=uid1)
    u2 = User.objects.get(uid=uid2)
    assert notification in u1.notifications
    assert notification in u2.notifications
    mock_parse_params.called_once_with(params)
    assert notification.inviter_id == 'inviter'
    assert notification.task_id == 'task'

    with pytest.raises(BadRequest):
        users = MagicMock()
        users.update.side_effect = Exception('General Exception')
        utils.insert_notification(users, notitype, params)
    with pytest.raises(BadRequest):
        mock_parse_params.return_value = {}
        utils.insert_notification(users, notitype, params)
    with pytest.raises(BadRequest):
        utils.insert_notification(users, 'whatever', params)


def test_parse_params():
    params = {'hello': 'world'}
    s = json.dumps(params)
    assert params == utils.parse_params(s)
    with pytest.raises(BadRequest):
        utils.parse_params('BadRequest')


def test_modify_player_id():
    uid = str(uuid4())
    player_id1 = str(uuid4())
    player_id2 = str(uuid4())
    with pytest.raises(DoesNotExist):
        u = User.objects.get(uid=uid)

    utils.modify_player_id(uid, player_id1)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 1
    assert str(u.player_ids[0]) == player_id1

    utils.modify_player_id(uid, player_id1)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 1
    assert str(u.player_ids[0]) == player_id1

    utils.modify_player_id(uid, player_id2)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 2
    assert str(u.player_ids[0]) == player_id1
    assert str(u.player_ids[1]) == player_id2

    utils.modify_player_id(uid, player_id2, register=False)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 1
    assert str(u.player_ids[0]) == player_id1

    utils.modify_player_id(uid, player_id2, register=False)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 1
    assert str(u.player_ids[0]) == player_id1

    utils.modify_player_id(uid, player_id1, register=False)
    u = User.objects.get(uid=uid)
    assert u is not None
    assert len(u.player_ids) == 0
