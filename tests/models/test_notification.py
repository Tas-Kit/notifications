import pytest
from mock import patch
from werkzeug.exceptions import BadRequest
from src.models import InvitationNotification


def nameredis_get_side_effect(key):
    if key == 'my_inviter_id':
        return 'my_inviter'.encode('utf-8')
    elif key == 'my_task_id':
        return 'my_task'.encode('utf-8')


class TestGenericNotification(object):

    def test_serialize(self):
        invitation = InvitationNotification(task_id='task_id', inviter_id='inviter_id').save()
        invitation.task_name = 'task_name'
        invitation.inviter_name = 'inviter_name'
        serialization = invitation.serialize()
        assert serialization['task_id'] == 'task_id'
        assert serialization['inviter_id'] == 'inviter_id'
        assert serialization['task_name'] == 'task_name'
        assert serialization['inviter_name'] == 'inviter_name'
        assert serialization['unread']
        assert serialization['nid'] == str(invitation.id)
        assert serialization['created'] == str(invitation.created)
        assert serialization['type'] == 'GenericNotification.InvitationNotification'
        assert serialization['contents'] == {
            'en': 'inviter_name invites you to join task_name.',
            'zh': 'inviter_name邀请你加入task_name。'
        }

    def test_get_contents(self):
        invitation = InvitationNotification()
        invitation.task_name = 'task_name'
        invitation.inviter_name = 'inviter_name'
        assert invitation.get_contents() == {
            'en': 'inviter_name invites you to join task_name.',
            'zh': 'inviter_name邀请你加入task_name。'
        }
        assert invitation.contents == {
            'en': '{inviter_name} invites you to join {task_name}.',
            'zh': '{inviter_name}邀请你加入{task_name}。'
        }

    @patch('src.nameredis.get', side_effect=nameredis_get_side_effect)
    def test_populate(self, mock_get):
        invitation = InvitationNotification(
            inviter_id='my_inviter_id',
            task_id='my_task_id'
        ).populate()
        assert 'my_inviter' == invitation.inviter_name
        assert 'my_task' == invitation.task_name
        mock_get.side_effect = Exception()
        with pytest.raises(BadRequest):
            invitation = InvitationNotification(
                inviter_id='my_inviter_id',
                task_id='my_task_id'
            ).populate()
