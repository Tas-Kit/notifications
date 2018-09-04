from mock import patch
from src.models import User, GenericNotification


class TestUser(object):

    @patch('src.utils.populate_name_cache')
    @patch('src.models.GenericNotification.serialize', side_effect=['a', 'b', 'c'])
    def test_serialize_notifications(self, mock_serialize, mock_populate_name_cache):
        user = User()
        user.notifications = [GenericNotification() for _ in range(3)]
        result = user.serialize_notifications()
        assert ['c', 'b', 'a'] == result
