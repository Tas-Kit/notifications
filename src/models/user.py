import mongoengine
from src import db
from src.models import GenericNotification


class User(db.Document):
    meta = {
        'indexes': [
            '#uid'
        ]
    }

    uid = db.StringField(max_length=40, required=True)
    player_ids = db.ListField(db.StringField(max_length=40, required=True))
    notifications = db.ListField(db.ReferenceField(GenericNotification, reverse_delete_rule=mongoengine.PULL))
