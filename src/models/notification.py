import datetime
from copy import deepcopy
from src import db, nameredis


class GenericNotification(db.Document):
    contents = {}
    meta = {
        'collection': 'notification',
        'allow_inheritance': True
    }

    created = db.DateTimeField(default=datetime.datetime.utcnow, required=True, null=False)
    unread = db.BooleanField(default=True, required=True, null=False)

    def get_id_attrs(self):
        return [attr for attr in dir(self) if attr.endswith('_id')]

    def get_name_dict(self):
        id_attrs = self.get_id_attrs()
        name_dict = {}
        for id_attr in id_attrs:
            id_value = getattr(self, id_attr)
            name = id_attr.replace('_id', '_name')
            name_dict[name] = nameredis.get(id_value)
            if name_dict[name] is not None:
                name_dict[name] = name_dict[name].decode('utf-8')
        return name_dict

    def get_contents(self):
        contents = deepcopy(self.contents)
        name_dict = self.get_name_dict()
        for lang, msg in self.contents.items():
            contents[lang] = msg.format(**name_dict)
        return contents


class InvitationNotification(GenericNotification):
    contents = {
        'en': '{inviter_name} invites you to join {task_name}.',
        'zh': '{inviter_name}邀请你加入{task_name}。'
    }
    _cls = 'InvitationNotification'

    inviter_id = db.StringField(max_length=40, required=True)
    task_id = db.StringField(max_length=40, required=True)
