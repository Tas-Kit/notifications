import pytest
import json
from requests.exceptions import HTTPError
from src import utils, name_cache
from src.models import User, InvitationNotification
from uuid import uuid4
from mongoengine.errors import DoesNotExist
from werkzeug.exceptions import BadRequest
from mock import patch, MagicMock


def test_get_data_ids():
    n1 = InvitationNotification(inviter_id='i1', task_id='t1')
    n2 = InvitationNotification(inviter_id='i2', task_id='t2')
    n3 = InvitationNotification(inviter_id='i3', task_id='t3')
    notis = [n1, n2, n3]
    assert set(['i1', 'i2', 'i3', 't1', 't2', 't3']) == set(utils.get_data_ids(notis))


@patch('src.utils.get_data_ids', return_value=['i1', 't1', 'i2', 't2', 'i3', 't3'])
@patch('src.nameredis.pipeline', return_value=MagicMock())
def test_populate_name_cache(mock_pipeline, mock_get_data_ids):
    mock_pipeline.return_value.execute.return_value = [
        'i1_value'.encode('utf-8'), 't1_value'.encode('utf-8'),
        'i2_value'.encode('utf-8'), 't2_value'.encode('utf-8'),
        'i3_value'.encode('utf-8'), 't3_value'.encode('utf-8')]
    n1 = InvitationNotification(inviter_id='i1', task_id='t1')
    n2 = InvitationNotification(inviter_id='i2', task_id='t2')
    n3 = InvitationNotification(inviter_id='i3', task_id='t3')
    notis = [n1, n2, n3]
    utils.populate_name_cache(notis)
    assert name_cache['i1'] == 'i1_value'
    assert name_cache['t1'] == 't1_value'
    assert name_cache['i2'] == 'i2_value'
    assert name_cache['t2'] == 't2_value'
    assert name_cache['i3'] == 'i3_value'
    assert name_cache['t3'] == 't3_value'


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


@patch('onesignalclient.notification.Notification')
@patch('src.onesignal_client.create_notification')
def test_send_notification(mock_send_notification, mock_notification):
    mock_notification.return_value = MagicMock()
    users = MagicMock()
    contents = {'en': 'hello'}
    notification = MagicMock()
    notification.get_contents.return_value = contents
    utils.send_notification(users, notification)
    mock_notification.called_once_with(contents)
    mock_send_notification.called_once()

    mock_send_notification.side_effect = HTTPError()
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


@patch('src.utils.parse_params', return_value={
    'inviter_id': 'inviter',
    'task_id': 'task'
})
def test_insert_notification(mock_parse_params):
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
