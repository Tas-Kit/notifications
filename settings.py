import os

ENV = os.getenv('ENV', 'DEV')
DEBUG = ENV != 'PROD'
PER_PAGE = os.getenv('PER_PAGE', 30)
# TASKSERVICE_HOST = os.getenv('TASKSERVICE_HOST', 'taskservice')
# TASKSERVICE_PORT = os.getenv('TASKSERVICE_HOST', '8000')
# TASKSERVICE_VERSION = os.getenv('TASKSERVICE_VERSION', 'v1')
# USERSERVICE_HOST = os.getenv('USERSERVICE_HOST', 'userservice')
# USERSERVICE_PORT = os.getenv('USERSERVICE_HOST', '8000')
# USERSERVICE_VERSION = os.getenv('USERSERVICE_VERSION', 'v1')


# # Target static dir
# COLLECT_STATIC_ROOT = './static'
# COLLECT_STORAGE = 'flask_collect.storage.file'

ONESIGNAL_USER_AUTH_KEY = os.environ.get('ONESIGNAL_USER_AUTH_KEY', '')
ONESIGNAL_APP_AUTH_KEY = os.environ.get('ONESIGNAL_APP_AUTH_KEY', '')
ONESIGNAL_APP_ID = os.environ.get('ONESIGNAL_APP_ID', '8c59edc2-8acf-4db9-9cc8-1095c0f10df8')

NAMEREDIS_HOST = os.environ.get('NAMEREDIS_HOST', 'nameredis')
NAMEREDIS_PORT = int(os.environ.get('NAMEREDIS_PORT', 6379))

MONGODB_SETTINGS = {
    'db': 'notifications',
    'host': os.environ.get('MONGODB_HOST', 'mongo'),
    'port': int(os.environ.get('MONGODB_PORT', 27017)),
    'username': os.environ.get('MONGODB_USERNMAE', 'root'),
    'password': os.environ.get('MONGODB_PASSWORD', 'abcd1234'),
    'authentication_source': 'admin'
}
