from src.models import InvitationNotification
from src import name_cache


def nameredis_get_side_effect(key):
    if key == 'my_inviter_id':
        return 'my_inviter'.encode('utf-8')
    elif key == 'my_task_id':
        return 'my_task'.encode('utf-8')


class TestGenericNotification(object):

    def test_serialize(self):
        name_cache.clear()
        name_cache['task_id'] = 'task_name'
        name_cache['inviter_id'] = 'inviter_name'
        invitation = InvitationNotification(task_id='task_id', inviter_id='inviter_id').save()
        serialization = invitation.serialize()
        assert serialization['task_id'] == 'task_id'
        assert serialization['inviter_id'] == 'inviter_id'
        assert serialization['nid'] == str(invitation.nid)
        assert serialization['created'] == str(invitation.created)
        assert serialization['type'] == 'GenericNotification.InvitationNotification'
        assert serialization['contents'] == {
            'en': 'inviter_name invites you to join task_name.',
            'zh': 'inviter_name邀请你加入task_name。'
        }

    def test_get_contents(self):
        name_cache.clear()
        name_cache['task_id'] = 'task_name'
        name_cache['inviter_id'] = 'inviter_name'
        invitation = InvitationNotification()
        invitation.task_id = 'task_id'
        invitation.inviter_id = 'inviter_id'
        assert invitation.get_contents() == {
            'en': 'inviter_name invites you to join task_name.',
            'zh': 'inviter_name邀请你加入task_name。'
        }
        assert invitation.contents == {
            'en': '{inviter_name} invites you to join {task_name}.',
            'zh': '{inviter_name}邀请你加入{task_name}。'
        }

    # @patch('src.nameredis.get', side_effect=nameredis_get_side_effect)
    # def test_populate(self, mock_get):
    #     invitation = InvitationNotification(
    #         inviter_id='my_inviter_id',
    #         task_id='my_task_id'
    #     ).populate()
    #     assert 'my_inviter' == invitation.inviter_name
    #     assert 'my_task' == invitation.task_name
    #     mock_get.side_effect = Exception()
    #     with pytest.raises(BadRequest):
    #         invitation = InvitationNotification(
    #             inviter_id='my_inviter_id',
    #             task_id='my_task_id'
    #         ).populate()
