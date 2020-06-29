#!/usr/bin/env python
import functools
import hashlib
import logging

import bson
import requests
import uuid
from flask import request, jsonify, make_response, Blueprint

import helper
from common.utils import get_local_now

lark_bp = Blueprint('login', __name__)

db = helper.get_mongodb()


def login_required(func):
    @functools.wraps(func)
    def decorated_func(*args, **kwargs):
        x_token = request.cookies.get('x-token')
        if not db.luckycat_users.find_one({'token': x_token}):
            response = make_response('need login', 401)
            return response

        return func(*args, **kwargs)

    return decorated_func


@lark_bp.route('/login', methods=['POST'])
def login():
    post_body = request.get_json(force=True, silent=True, cache=False)
    email = post_body.get('email', '')
    password = post_body.get('password', '')
    password = hashlib.sha1(password.encode('utf-8')).hexdigest()
    user = db.luckycat_users.find_one({'email': email, 'password': password})
    if user:  # query db
        response = make_response(jsonify({
            'success': True,
            'code': 0,
            'msg': 'login succeed',
        }), 200)
        response.set_cookie('x-token', user.get('token', ''))
        return response
    else:
        return jsonify({
            'success': False,
            'code': 405,
            'msg': 'password is wrong or no such user,you should set your password by feishu login',
        })


@lark_bp.route('/lark_login', methods=['get'])
def lark_login():
    # 生成登录预授权码 code，拼接 code 和 state 参数重定向至 redirect_uri
    code = request.args.get('code')
    logging.info(f'login with code {code}')

    url = f'http://lark.geezcomics.com/lark/lark_login_true?code={code}'
    loginInfo = requests.get(url).json()
    logging.info(loginInfo)
    user = loginInfo.get('data')
    if user:
        user['token'] = code
        if db.luckycat_users.find_one({'open_id': user['open_id']}):
            del user['_id']  # 保留原生成的_id
        else:
            user['_id'] = bson.ObjectId(user['_id'])
        db.luckycat_users.update_one({'open_id': user['open_id']}, {'$set': user}, upsert=True)
        if '_id' in user: del user['_id']
        response = make_response(jsonify({
            'success': True,
            'code': 0,
            'msg': 'login succeed',
            'data': user
        }), 200)

        response.set_cookie('x-token', code)
        db.logs.insert_one({'username': user.get('name'), 'action': 'login', 'datetime': get_local_now()})
        return response
    else:
        return jsonify({
            'success': False,
            'code': 405,
            'msg': 'not authened',
        })


@lark_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    response = make_response(jsonify({
        'success': True,
        'code': 0,
        'msg': 'logout success'
    }), 200)

    x_token = request.cookies.get('x-token')
    new_token = str(uuid.uuid4())
    db.luckycat_users.update({'token': x_token}, {'$set': {'token': new_token}}, multi=True)
    response.set_cookie('x-token', '')
    return response


@lark_bp.route('/userinfo', methods=['get'])
@login_required
def get_userinfo():
    res = {
        'success': True,
        'code': 0,
        'msg': 'success',
        'data': {}
    }

    x_token = request.cookies.get('x-token')

    user = db.luckycat_users.find_one({'token': x_token})
    res['data'] = user
    return jsonify(res)
