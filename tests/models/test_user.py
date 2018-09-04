from mock import patch, MagicMock
from src.models import User, GenericNotification


class TestUser(object):

    @patch('src.models.GenericNotification.serialize', side_effect=['a','b','c'])
    def test_serialize_notifications(self, mock_serialize):
        user = User()
        user.notifications = [GenericNotification() for _ in range(3)]
        result = user.serialize_notifications()
        assert ['a', 'b', 'c'] == result
