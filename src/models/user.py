import mongoengine
from settings import PER_PAGE
from src import db, utils
from src.models import GenericNotification


class User(db.Document):
    uid = db.UUIDField(required=True, primary_key=True)
    player_ids = db.ListField(db.UUIDField(required=True))
    notifications = db.ListField(db.ReferenceField(GenericNotification, reverse_delete_rule=mongoengine.PULL))

    def serialize_notifications(self):
        notifications = self.notifications[-PER_PAGE:]
        utils.populate_name_cache(notifications)
        serialized_notifications = []
        for notification in notifications:
            serialized_notifications.append(notification.serialize())
        return serialized_notifications[::-1]
