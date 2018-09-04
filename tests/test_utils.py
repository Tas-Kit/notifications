import pytest
import json
from src import utils
from src.models import User
from uuid import uuid4
from mongoengine.errors import DoesNotExist
from werkzeug.exceptions import BadRequest


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
