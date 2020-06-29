import logging
import os
import pymongo
import toml

_CONFIG = {}
_CONFIG.update(toml.load('config/' + 'novel.toml'))
_CONFIG.update(toml.load('config/' + os.getenv('ENV', 'local') + '.toml'))

logging.basicConfig(
    format=_CONFIG['default']['log_format'],
    level=getattr(logging, _CONFIG['default']['log_level'].upper())
)

_connection = pymongo.MongoClient(
    _CONFIG['mongodb']['url'],
    replicaSet=_CONFIG['mongodb']['replica_set'],
    tz_aware=True,
    connect=False,
    read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED,
)

_db = _connection[_CONFIG['mongodb']['database']]
if _CONFIG['mongodb']['auth']:
    _db.authenticate(_CONFIG['mongodb']['user'], _CONFIG['mongodb']['pass'])


def get_config():
    return _CONFIG


def get_mongodb():
    return _db

