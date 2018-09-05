import mongoengine
from settings import PER_PAGE
from src import db, utils
from src.models import GenericNotification


class User(db.Document):
    uid = db.UUIDField(required=True, primary_key=True)
    player_ids = db.ListField(db.UUIDField(required=True))
    read = db.MapField(field=db.BooleanField(default=False, required=True))
    notifications = db.ListField(db.ReferenceField(GenericNotification, reverse_delete_rule=mongoengine.PULL))

    def serialize_notifications(self):
        notifications = self.notifications[-PER_PAGE:]
        utils.populate_name_cache(notifications)
        serialized_notifications = []
        for notification in notifications:
            serialized_notification = notification.serialize()
            if str(notification.nid) not in self.read:
                serialized_notification['read'] = False
                self.read[str(notification.nid)] = True
            else:
                serialized_notification['read'] = True
            serialized_notifications.append(serialized_notification)
        self.update(read=self.read)
        return serialized_notifications[::-1]
