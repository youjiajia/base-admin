import json
import logging
import uuid

import requests
import helper


ALL_COMPANY = ['webeye', 'jxhz']


class SyncUser():
    def __init__(self, company='webeye'):
        self.company = company
        if self.company == 'webeye':
            self.APP_ID = 'cli_9ed5d5bde42a900e'
            self.APP_SECRET = 'gTgdm00wCqfIbk67m6EJ5fdUSt7IVads'
        # 捷新汇智
        elif self.company == 'jxhz':
            self.APP_ID = 'cli_9e1d009dd4e9d00d'
            self.APP_SECRET = '1iMGJp0bCeBPNeEUSjLu2eE1L4BUTqaN'
        self.department_map = {}
        self.all_users = []
        self.db = helper.get_mongodb()

    def run(self):
        self.get_access_token()
        self.get_departments_and_users()
        logging.info('#############################################')
        logging.info(self.all_users)
        self.save_to_db()
        logging.info('Successfully sync api users.')

    def get_access_token(self):
        resp = requests.post(
            url='https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'app_id': self.APP_ID,
                'app_secret': self.APP_SECRET,
            })
        )
        if resp.status_code != 200:
            raise Exception('get_access_token, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json.get('tenant_access_token'):
            raise Exception('get_access_token, code: %s, msg: %s' % (resp.status_code, resp.content))

        self.tenant_access_token = resp_json['tenant_access_token']

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.tenant_access_token)
        }

    def get_departments_and_users(self):
        '''
        https://open.feishu.cn/document/ukTMukTMukTM/ugjNz4CO2MjL4YzM
        {
            "code": 0,
            "msg": "success",
            "data": {
                "authed_departments": [
                    "od-ae39090ee451cb3f87d3e15142d3c7e7",
                    "od-4159df34fb9b0191b8610842493607d3",
                    "od-0c4d627c28d0d92091685ff4465dd43d",
                    "od-d308ce88c2e3678afcfd0fe5a0400716",
                    "od-2a404ae49e3c69e267fc8e08ed946b30",
                    "od-b2215870b97d52ab7df94340bae48b24",
                    "od-48eb70defefdd89d840c25ad88a87607",
                    "od-aecb44972ad19e047edbd19cbef71b3b",
                    "od-add8d48196a823d7b432a34c9e8cea33"
                ],
                "authed_employee_ids": [
                    "8d177562"
                ],
                "authed_open_ids": [
                    "ou_efebdd33fcc28035796c00213ca60801"
                ]
            }
        }
        '''

        def _get_user_info_json(u):
            return {
                'open_id': u['open_id'],
                'employee_id': u['employee_id'],
                'name': u['name'],
                'avatar': u['avatar_url'],
                'email': u['email'],
                'employee_no': u.get('employee_no', ''),
                'status': u.get('status', 0)
            }

        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/scope/get',
            headers=self.get_headers(),
        )
        if resp.status_code != 200:
            raise Exception('get all departments fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        logging.info(resp_json)
        authed_open_ids = resp_json['data'].get('authed_open_ids', [])
        # add boss employee_id (8d177562) to user list.
        # for u in self.get_user_info_by_openids(authed_open_ids):
        #     logging.info(u)
        #     self.all_users.append({**_get_user_info_json(u), **{'department': 'Webeye'}})

        group_list = self.get_department_info(resp_json['data'].get('authed_departments', []))
        for group in group_list:
            self.department_map[group['id']] = group['name']
            logging.info('get_sub_demaprment of {}'.format(group['name']))
            group['departments'] = self.get_sub_departments(group['id'])
            for dept in group['departments']:
                self.department_map[dept['id']] = '{}-{}'.format(group['name'], dept['name'])

        for group in group_list:
            group_users = self.get_group_users(group['id'])
            logging.info('get_users of {} {}'.format(group['name'], len(group_users)))
            for u in group_users:
                dpt_ids = u['departments']
                self.all_users.append({**_get_user_info_json(u), **{
                    'department': self.department_map.get(dpt_ids[0] if dpt_ids else group['id'])}})

        logging.info('total user {}'.format(len(self.all_users)))

    def get_department_info(self, dpt_id_list):
        '''
        https://open.feishu.cn/document/ukTMukTMukTM/uczN3QjL3czN04yN3cDN
        '''
        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/department/detail/batch_get',
            headers=self.get_headers(),
            params={
                'department_ids': dpt_id_list
            }
        )
        if resp.status_code != 200:
            raise Exception('get all departments fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json['data'] or not resp_json.get('data', []).get('department_infos'):
            raise Exception('get all departments fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        return resp_json['data']['department_infos']

    def get_sub_departments(self, g_id):
        '''
        https://open.feishu.cn/document/ukTMukTMukTM/ugzN3QjL4czN04CO3cDN
        {
            "code": 0,
            "msg": "success",
            "data": {
                "department_infos": [
                    {
                        "id": "od-16a6c4ceb430f42cd508bf38b39673bd",
                        "name": "Product",
                        "parent_id": "od-ae39090ee451cb3f87d3e15142d3c7e7"
                    },
                    {
                        "id": "od-d916f215f1bcd0b5fe3853124c9f401d",
                        "name": "Satori AI",
                        "parent_id": "od-ae39090ee451cb3f87d3e15142d3c7e7"
                    },
                    {
                        "id": "od-ced4b10ffd1cf549f367673d8d269210",
                        "name": "Satori BI",
                        "parent_id": "od-ae39090ee451cb3f87d3e15142d3c7e7"
                    }
                ],
                "has_more": false
            }
        }
        '''
        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/department/simple/list',
            headers=self.get_headers(),
            params={
                'department_id': g_id,
                'offset': 0,
                'page_size': 100,
            }
        )
        if resp.status_code != 200:
            raise Exception('get_sub_departments fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json['data']:
            raise Exception('get_sub_departments, code: %s, msg: %s' % (resp.status_code, resp.content))

        return resp_json['data'].get('department_infos', [])

    def get_group_users(self, group_id):
        '''
        https://open.feishu.cn/open-apis/contact/v1/department/user/detail/list?
        {
        "code": 0,
        "msg": "success",
        "data": {
            "has_more": false,
            "user_list": [
                {
                    "employee_id": "g93b2gg1",
                    "employee_no": "1293",
                    "name": "石永刚",
                    "open_id": "ou_fdcc0757aa10c47bab96ce051f8f34b5"
                },
                {
                    "employee_id": "d2ff8ge1",
                    "employee_no": "1262",
                    "name": "王翔",
                    "open_id": "ou_c47e6fd298317e24f608690feb5e8c1c"
                },
        '''

        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/department/user/detail/list',
            headers=self.get_headers(),
            params={
                'department_id': group_id,
                'offset': 0,
                'page_size': 100,
                'fetch_child': True
            }
        )
        if resp.status_code != 200:
            raise Exception('get_group_users fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json['data']:
            raise Exception('get_group_users, code: %s, msg: %s' % (resp.status_code, resp.content))

        # TODO: handle has_more in future
        return resp_json['data'].get('user_infos', [])

    def get_user_info_by_openids(self, open_ids):
        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/user/batch_get',
            headers=self.get_headers(),
            params={
                'open_ids': open_ids
            }
        )
        if resp.status_code != 200:
            raise Exception('get_user_info fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json['data']:
            raise Exception('get_user_info, code: %s, msg: %s' % (resp.status_code, resp.content))

        # TODO: handle has_more in future
        return resp_json['data']['user_infos']

    def get_user_info_by_ids(self, employee_ids):
        resp = requests.get(
            url='https://open.feishu.cn/open-apis/contact/v1/user/batch_get',
            headers=self.get_headers(),
            params={
                'employee_ids': employee_ids
            }
        )
        if resp.status_code != 200:
            raise Exception('get_user_info fail, code: %s, msg: %s' % (resp.status_code, resp.content))

        resp_json = resp.json()
        if resp_json['code'] != 0 or not resp_json['data']:
            raise Exception('get_user_info, code: %s, msg: %s' % (resp.status_code, resp.content))

        # TODO: handle has_more in future
        return resp_json['data']['user_infos']

    def save_to_db(self):
        for user in self.all_users:
            query = self.db.luckycat_users.find_one({'open_id': user['open_id']})
            profile = {}
            if query:
                profile = query
            profile['email'] = user.get('email', '')
            profile['open_id'] = user['open_id']
            profile['name'] = user['name']
            profile['avatar'] = user['avatar']
            profile['department'] = user.get('department').split(' ')[0]
            profile['webeye'] = 1 if self.company == 'webeye' else 0
            # profile['admin_app'] = []  # 存appid
            # profile['auth_app'] = []
            #
            # auth_name = ['付晶晶', '乔婷婷', '陈雪莹', '张烨', '李媛', '谢紫莹', '苏鹏', '叶磊', '韩昆彤', '邵家松']
            # profile['auth'] = 1 if user['name'] in auth_name else 0
            #
            # admin_name = []
            # profile['admin'] = 1 if user['name'] in admin_name else 0

            profile['token'] = str(uuid.uuid4())
            profile['roles'] = profile.get('roles', [])

            if user['status'] == 0:  # 用户状态，bit0(最低位): 1冻结，0未冻结；bit1:1离职，0在职；bit2:1未激活，0已激活
                logging.info('save {} {}'.format(user['name'], user['open_id']))
                profile['is_active'] = True
            else:
                profile['is_active'] = False
            self.db.luckycat_users.update_one({'open_id': user['open_id']}, {'$set': profile}, upsert=True)

        # logging.info('current normal user count {}'.format(len(valid_open_ids)))

    def get_app_access_token(self):
        url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/'
        header = {'Content-Type': 'application/json'}
        data = {"app_id": self.APP_ID,
                "app_secret": self.APP_SECRET}
        response = requests.post(url, json=data, headers=header).json()
        logging.info(response)
        if response.get('code') == 0:
            return response.get('app_access_token')

    def get_user_authen(self, code):
        url = 'https://open.feishu.cn/open-apis/authen/v1/access_token'
        header = {'Content-Type': 'application/json'}
        data = {"app_access_token": self.get_app_access_token(),
                "grant_type": 'authorization_code',
                "code": code}
        response = requests.post(url, json=data, headers=header).json()
        print('get_user_authen:', response)
        if response.get('code') == 0:
            return response.get('data')
        return response

    def lark_auth_check(self, code):
        data = self.get_user_authen(code)
        open_id = data.get('open_id')
        return open_id

    def get_user_info(self, code):
        url = 'https://open.feishu.cn/open-apis/authen/v1/user_info'
        header = {'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + get_user_authen(code).get('access_token')
                  }
        response = requests.get(url, headers=header)
        logging.info(response.text)
        response = response.json()
        if response.get('code') == 0:
            return response.get('data')
        return response


if __name__ == '__main__':
    # get data from feishu
    for company in ALL_COMPANY:
        SyncUser(company=company).run()
