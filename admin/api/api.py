import traceback

from flask import Blueprint, request, jsonify, make_response
import requests

import helper
from common.utils import login_required, get_local_now
from common.const import PROVIDERS


app_bp = Blueprint('app', __name__)
db = helper.get_mongodb()


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
