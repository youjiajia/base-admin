import json

import requests

from common.utils import get_local_now


class ApiLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            body = json.loads(request.body)
        except Exception:
            body = dict()
        body.update(dict(request.POST))
        response = self.get_response(request)
        user = {}
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")
        user.update({'ip', ip})
        log = {
            "product_code": '',
            "product_sub_code": request.META.get('product'),
            'product_name': '',  # whale comic video
            'user_info': user,
            "event_type": request.path,
            'request_method': request.method,
            'create_time': get_local_now(),
            'payload': body
        }
        # 发送到日志平台
        requests.post('url', json=log)
        return response
