from mock import patch
from src.models import User, GenericNotification


class TestUser(object):

    @patch('src.models.User.update')
    @patch('src.utils.populate_name_cache')
    @patch('src.models.GenericNotification.serialize',
           side_effect=[{'a': 1},
                        {'b': 2},
                        {'c': 3}])
    def test_serialize_notifications(self, mock_serialize, mock_populate_name_cache, mock_update):
        user = User()
        user.notifications = [GenericNotification() for _ in range(3)]
        result = user.serialize_notifications()
        assert mock_update.called_once()
        assert result == [{'c': 3,
                           'read': False},
                          {'b': 2,
                           'read': False},
                          {'a': 1,
                           'read': False}]
