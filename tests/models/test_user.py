from uuid import uuid4
from mock import patch
from src import utils
from src.models import User, GenericNotification, InvitationNotification


class TestUser(object):

    @patch('src.models.User.update')
    def test_read_notifications(self, mock_update):
        uid = uuid4()
        user = User(uid=uid).save()
        user.notifications = [
            InvitationNotification(
                inviter_id='i' + str(i),
                task_id='t' + str(i)).save()
            for i in range(3)]
        user.read_notifications()
        user = utils.get_user(uid)
        for notification in user.notifications:
            assert user.read[notification.nid]

    @patch('src.utils.populate_name_cache')
    @patch('src.models.GenericNotification.serialize',
           side_effect=[{'a': 1},
                        {'b': 2},
                        {'c': 3}])
    def test_serialize_notifications(self, mock_serialize, mock_populate_name_cache):
        user = User()
        user.notifications = [GenericNotification() for _ in range(3)]
        result = user.serialize_notifications()
        assert result == [{'c': 3,
                           'read': False},
                          {'b': 2,
                           'read': False},
                          {'a': 1,
                           'read': False}]
