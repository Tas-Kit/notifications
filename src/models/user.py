import mongoengine
from settings import PER_PAGE
from src import db, utils
from src.models import GenericNotification


class User(db.Document):
    uid = db.UUIDField(required=True, primary_key=True)
    player_ids = db.ListField(db.UUIDField(required=True))
    read = db.MapField(field=db.BooleanField(default=False, required=True))
    notifications = db.ListField(db.ReferenceField(GenericNotification, reverse_delete_rule=mongoengine.PULL))

    def read_notifications(self):
        for notification in self.notifications:
            self.read[str(notification.id)] = True
        self.update(read=self.read)

    def serialize_notifications(self):
        notifications = self.notifications[-PER_PAGE:]
        utils.populate_name_cache(notifications)
        serialized_notifications = []
        for notification in notifications:
            serialized_notification = notification.serialize()
            read = str(notification.nid) in self.read
            serialized_notification['read'] = read
            serialized_notifications.append(serialized_notification)
        return serialized_notifications[::-1]
