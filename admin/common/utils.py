import functools
from datetime import datetime
import random
import string

from dateutil import *
from flask import request, make_response

import helper as _helper

_config = _helper.get_config()

# _storage_config = _config['storage']
# _encrypt_key = _config['novel']['encrypt_key'].encode('utf-8')

_local_zone = tz.tzlocal()
_db = _helper.get_mongodb()


def get_local_now():
    return datetime.now().replace(tzinfo=_local_zone)


def radom_name(length=8):
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def login_required(func):
    @functools.wraps(func)
    def decorated_func(*args, **kwargs):
        x_token = request.cookies.get('x-token')
        if not _db.luckycat_users.find_one({'token': x_token}):
            response = make_response('need login', 401)
            return response

        return func(*args, **kwargs)

    return decorated_func


def log_operation(func):
    @functools.wraps(func)
    def decorated_func(*args, **kwargs):
        x_token = request.cookies.get('x-token')
        user = _db.luckycat_users.find_one({'token': x_token})
        func_name = func.__name__
        print('user:', user, func_name)
        post_json = request.get_json(force=True, silent=True, cache=True)  # cache=True must
        if not post_json:
            post_json = {}
        log = {
               'username': user.get('name') or user.get('username') if user else 'unknown',
               'action': func_name,
               'datetime': get_local_now()
               }
        if not func_name.startswith('user'):
            log = {
                   'id': post_json.get('id'),
                   'app': post_json.get('app') or post_json.get('code'),
                   'k': post_json.get('k') or post_json.get('name'),
                   }
        if func_name.startswith('user'):
            # only one once
            for item in post_json:
                log['app'] = item['appid']
                log['k'] = item['admins']

        _db.logs.insert_one(log)
        return func(*args, **kwargs)

    return decorated_func
