import traceback
import logging
from collections import defaultdict

import pandas as pd
import calendar

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from flask import Blueprint, request, jsonify, make_response
import requests

import helper
from common.utils import login_required, get_local_now
from common.const import PROVIDERS


app_bp = Blueprint('app', __name__)
db = helper.get_mongodb()


@app_bp.route('/bill_add', methods=['post'])
@login_required
def bill_add():
    result = {
        'success': True,
        'code': 0,
        'msg': '',
        'data': []
    }
    try:
        post_body = request.get_json(force=True, silent=True, cache=False)
        post_body['created_at'] = get_local_now()
        bill_date = post_body.get('bill_date')
        db.bill.insert_one(post_body)  # 保存账单参数
    except Exception as e:
        result = {
            'success': False,
            'code': 1,
            'msg': str(e),
            'data': []
        }
        traceback.print_exc()
    return jsonify(result)


@app_bp.route('/config_detail', methods=['post'])
# @login_required
def bill_config_detail():
    result = {
        'success': True,
        'code': 0,
        'msg': '',
        'data': []
    }
    try:
        post_body = request.get_json(force=True, silent=True, cache=False)
        bill_date = post_body.get('bill_date')
        config = db.bill.find_one({'bill_date': bill_date})  # 保存账单参数
        result['data'] = config
    except Exception as e:
        result = {
            'success': False,
            'code': 1,
            'msg': str(e),
            'data': []
        }
        traceback.print_exc()
    return jsonify(result)


@app_bp.route('/config_update', methods=['post'])
@login_required
def bill_config_update():
    result = {
        'success': True,
        'code': 0,
        'msg': '',
        'data': []
    }
    try:
        post_body = request.get_json(force=True, silent=True, cache=False)
        bill_date = post_body.get('bill_date')
        del post_body['_id']
        db.bill.update_one({'bill_date': bill_date}, {
                           '$set': post_body}, upsert=True)  # 更新账单参数
        db.cache_data.remove({'bill_date': bill_date})
    except Exception as e:
        result = {
            'success': False,
            'code': 1,
            'msg': str(e),
            'data': []
        }
        traceback.print_exc()
    return jsonify(result)


@app_bp.route('/bill_detail', methods=['post'])
@login_required
def bill_detail():
    result = {
        'success': True,
        'code': 0,
        'msg': '',
        'data': []
    }
    try:
        post_body = request.get_json(force=True, silent=True, cache=False)
        bill_date = post_body.get('bill_date')  # yearmonth
        is_novel = post_body.get('is_novel', '')
        is_novel = True   # if is_novel == True else False
        if db.bill.find_one({'bill_date': bill_date}):
            provider_revisions = get_data(bill_date, is_novel)
            result['data'] = provider_revisions

        return jsonify(result)
    except Exception as e:
        result = {
            'success': False,
            'code': 1,
            'msg': str(e),
            'data': []
        }
        traceback.print_exc()
    return jsonify(result)


@app_bp.route('/bill_export', methods=['get'])
@login_required
def bill_export():
    result = {
        'success': True,
        'code': 0,
        'msg': '',
        'data': []
    }
    try:
        bill_date = request.args.get('bill_date')
        is_novel = request.args.get('is_novel')
        provider = request.args.get('provider')
        is_pv = request.args.get('pv')
        is_novel = True if is_novel == 'true' else False
        is_pv = True if is_pv == 'true' else False
        data = get_data(bill_date, is_novel)
        headers = ['CP名称', 'PV', '分成']
        title = 'CP分成'
        keys = ['cp_name', 'pv', 'earn']
        if is_novel:
            title = PROVIDERS.get(provider) + '-' + provider
            keys = ['name', 'pv', 'earn']
            headers = ['书名', 'PV', '分成']
            logging.info(data)
            provider_keys = {item['cp_code']: item for item in data} if data else {}
            data = provider_keys.get(provider, {}).get('items', [])
        if not is_pv:
            headers.remove('PV')
            keys.remove('pv')
        book = Workbook()
        sheet1 = book.active
        sheet1.title = title
        sheet1.append(headers)
        for line in data:
            sheet1.append([v for k, v in line.items() if k in keys])
        content = save_virtual_workbook(book)
        response = make_response(content)  # tablib不能处理过大的数据  32767
        response.headers['Content-Type'] = 'application/vnd.ms-excel'
        filename = f'{title}-{bill_date}.xlsx'
        from urllib.parse import quote
        response.headers['Content-Disposition'] = "attachment; filename={0};filename*=utf-8''{0}".format(quote(filename))
        # response.headers['x-suggest-filename'] = filename
        return response

    except Exception as e:
        result = {
            'success': False,
            'code': 1,
            'msg': str(e),
            'data': []
        }
        traceback.print_exc()
    return jsonify(result)


def get_data(bill_date, is_novel):
    cached = db.cache_data.find_one({'bill_date': bill_date})
    if cached:
        del cached['_id']
        del cached['bill_date']
        if not is_novel:
            temp = []
            for item in cached['data']:
                del item['items']
                temp.append(item)
            cached['data'] = temp
        return cached['data']
    bill = db.bill.find_one({'bill_date': bill_date})
    sort = [('created_at', -1), ]
    if not bill:
        bill = db.bill.find_one({}, sort=sort)
        del bill['_id']
        bill['created_at'] = get_local_now()
        bill['bill_date'] = bill_date
        db.bill.save(bill)
        bill = db.bill.find_one({'bill_date': bill_date})
    total = bill.get('total')  # 资金池总量
    # percent_own = bill.get('percent', 0.5)  # 自己的分成比例
    # percent_provider = 1 - percent_own
    year = bill_date[:4]
    month = bill_date[4:]
    days = calendar.monthrange(int(year), int(month))[1]
    start_date = '-'.join([year, month, '01'])
    end_date = '-'.join([year, month, str(days)])

    data = db.luckycat_data.find_one({'bill_date': bill_date})
    if not data:
        data = requests.get(
            'http://ec2-161-189-192-143.cn-northwest-1.compute.amazonaws.com.cn/api/queries/122/results.json?api_key=gzTwA5MqAtmT2IDyTde8aSD6yndUAWa14iwgakZF').json()
    data = pd.DataFrame(data['query_result']['data']['rows'])  # pd.read_json('data.json')

    providers_pv = defaultdict(int)
    providers_books = defaultdict(list)

    for index, row in data.iterrows():
        name = row['e_page']
        providers = db.books.find({'name': name}, {'provider': 1})
        for item in providers:
            provider = item['provider']
            providers_pv[provider] += row['pv']
            providers_books[provider].append(
                {'name': name, 'pv': row['pv']})
    print(providers_pv)
    # 计算比例
    total_pv = sum(providers_pv.values())
    # 1. prvider
    provider_revisions = []
    config_list = bill.get('items')
    provicer_config = {item['cp_code']: item for item in config_list} if config_list else {}

    for k, v in providers_pv.items():
        percentage = provicer_config.get(k).get(
            'percentage', 0.5) if provicer_config.get(k) else 0.5
        base_revision = provicer_config.get(k).get(
            'base', 0) if provicer_config.get(k) else 0
        book_earn = []
        for book in providers_books[k]:
            book['earn'] = round(
                book['pv'] / total_pv * percentage * total, 2)
            book_earn.append(book)
        earn = round(v / total_pv * percentage * total, 2)
        provider_revisions.append({
            'cp_name': PROVIDERS.get(k),
            'cp_code': k,
            'pv': v,
            'earn': earn,
            'gain': round(v / total_pv * total, 2),
            'base_revision': earn if earn > base_revision else base_revision,  # base_revision,
            'items': book_earn
        })
    cached = {'bill_date': bill_date, 'data': provider_revisions}
    db.cache_data.update_one({'bill_date': bill_date}, {'$set': cached}, upsert=True)
    if not is_novel:
        temp = []
        for item in provider_revisions:
            del item['items']
            temp.append(item)
        provider_revisions = temp
    return provider_revisions
