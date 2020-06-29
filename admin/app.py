import json
from datetime import datetime

import requests
from apscheduler.triggers.cron import CronTrigger
from bson import ObjectId
from flask.json import JSONEncoder
from flask import request, g, jsonify, make_response
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import helper
import flask
import logging
import sys
from common.utils import get_local_now

from api.login import lark_bp
from api.api import app_bp

if sys.version_info.major == 3 and sys.version_info.minor < 7:
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()


class _CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(obj, ObjectId):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


config = helper.get_config()
app = flask.Flask(__name__)
app.json_encoder = _CustomJSONEncoder
_db = helper.get_mongodb()
scheduler = APScheduler()


def set_data_config():
    # 取出来就是上个月的数据
    data = requests.get('http://ec2-161-189-192-143.cn-northwest-1.compute.amazonaws.com.cn/api/queries/122/results.json?api_key=gzTwA5MqAtmT2IDyTde8aSD6yndUAWa14iwgakZF').json()
    bill_date = datetime.now().strftime('%Y-%m-%d')
    data.update({'bill_date': bill_date})
    _db.luckycat_data.update_one({'bill_date': bill_date}, {'$set': data}, upsert=True)
    from api.api import get_data
    get_data(bill_date, False)


@app.before_request
def before_request_hook():
    x_token = request.cookies.get('x-token')
    user = _db.luckycat_users.find_one({'token': x_token}) or {}
    path = request.path
    method = request.method
    try:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    except Exception as e:
        ip = request.remote_addr
    user.update({'ip': ip})
    post_json = request.get_json(force=True, silent=True, cache=True)  # cache=True must
    if not post_json:
        post_json = {}
    log = {
        "product_code": '',
        "product_sub_code": request.headers.get('product'),
        'product_name': '',
        'user_info': user,
        "event_type": path,
        'request_method': method,
        'create_time': get_local_now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': post_json
    }
    # logging.info(log)
    g.operation_log = log
    # _db.logs.insert_one(log)


@app.after_request
def after_request_hook(response):
    # response is a WSGI object, and that means the body of the response must be an iterable
    # 不出异常才会调用  405不属于异常 返回不正常值的要记录吗？？？？
    # logging.info(response.get_data(as_text=True))  # 返回的响应内容
    d = response.get_json()  # 不是json数据 就为空  登陆要记录吗（也是json  附加cookie 不在get_data 中） 是个特殊的

    log = g.operation_log
    path = log.get('event_type', '').split('/')[-1]
    NOT_LOGGED = ['bill_export']
    if path not in NOT_LOGGED and d:
        response_json = d  # json.loads(d)
        if response_json.get('code') == 0:
            # requests.post('http://52.83.83.23/api/log_add', json=log)
            pass
    return response


@app.route('/')
def hello():
    return 'hello world'


@app.route('/hi')
def hi():
    # make_response 另加headers： Set-Cookie: x-token=jshalajkkasjdn; Path=/  不在 data body中
    response = make_response(jsonify({
        'success': True,
        'code': 0,
        'msg': 'login succeed1111',
    }), 200)
    response.set_cookie('x-token', 'jshalajkkasjdn')
    logging.info(request.args.get('pv'))
    return response


app.register_blueprint(lark_bp, url_prefix='/api')
app.register_blueprint(app_bp, url_prefix='/api')


def _main():
    scheduler.add_job(id='1', func=set_data_config, trigger='cron', minute='0', hour='12', day='1', month='*', day_of_week='*')
    scheduler.init_app(app=app)
    scheduler.start()

    port = sys.argv[1] if len(sys.argv) > 1 else config['flask']['port']
    host = config['flask']['host']
    debug = config['flask']['debug']
    logging.info('host=%r, port=%r' % (host, port))
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    _main()
