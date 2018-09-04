import datetime
from copy import deepcopy
from src import db, nameredis, utils
from src.constants import ERROR_CODE


class GenericNotification(db.Document):
    contents = {}
    meta = {
        'collection': 'notification',
        'allow_inheritance': True
    }

    created = db.DateTimeField(default=datetime.datetime.utcnow, required=True, null=False)
    unread = db.BooleanField(default=True, required=True)

    def populate(self):
        try:
            for key, name in self.params.items():
                attr_id = getattr(self, key)
                value = nameredis.get(attr_id)
                if value is not None:
                    setattr(self, name, value.decode('utf-8'))
            return self
        except Exception as e:
            utils.handle_error(e, ERROR_CODE.NAMEREDIS_ERROR)

    def get_contents(self):
        contents = deepcopy(self.contents)
        params = {
            name: getattr(self, name, 'None')
            for name in self.params.values()
        }
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
    inviter_name = db.StringField(max_length=100)
    task_name = db.StringField(max_length=100)
