from uuid import uuid4
import datetime
from copy import deepcopy
from src import db, name_cache


class GenericNotification(db.Document):
    contents = {}
    meta = {
        'collection': 'notification',
        'allow_inheritance': True
    }

    nid = db.UUIDField(default=uuid4, primary_key=True)
    created = db.DateTimeField(default=datetime.datetime.utcnow, required=True, null=False)

    def serialize(self):
        data = {}
        for key, value in self.params.items():
            data[key] = getattr(self, key)
        data['nid'] = str(self.nid)
        data['type'] = self._cls
        data['contents'] = self.get_contents()
        data['created'] = str(self.created)
        return data

    def get_contents(self):
        contents = deepcopy(self.contents)
        params = {}
        for id_name, value_name in self.params.items():
            id_data = getattr(self, id_name)
            params[value_name] = name_cache[id_data]
        for lang, msg in self.contents.items():
            contents[lang] = msg.format(**params)
        return contents


class InvitationNotification(GenericNotification):
    params = {
        'inviter_id': 'inviter_name',
        'task_id': 'task_name'
    }

    contents = {
        'en': '{inviter_name} invites you to join {task_name}.',
        'zh': '{inviter_name}邀请你加入{task_name}。'
    }
    _cls = 'InvitationNotification'

    inviter_id = db.StringField(max_length=40, required=True, null=False)
    task_id = db.StringField(max_length=40, required=True, null=False)
