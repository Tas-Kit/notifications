import mongoengine
from src import db
from src.models import GenericNotification


class User(db.Document):
    uid = db.UUIDField(required=True, primary_key=True)
    player_ids = db.ListField(db.UUIDField(required=True))
    notifications = db.ListField(db.ReferenceField(GenericNotification, reverse_delete_rule=mongoengine.PULL))

    def serialize_notifications(self):
        notifications = []
        for notification in self.notifications:
            notifications.append(notification.serialize())
        return notifications
