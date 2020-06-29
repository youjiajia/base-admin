#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=too-many-statements, line-too-long

import helper
import json

_config = helper.get_config()

# Finished status
FINISHED_STATUS_YES = 1
FINISHED_STATUS_NO = 2

# Rankings
RANK_TYPE_HOMEPAGE = 1
RANK_TYPE_CATEGORY = 2
RANK_TYPE_FINISHED = 3
RANK_TYPE_SEARCH = 4

# Categories
CATEGORIES = json.loads(_config['novel']['categories'])
CATEGORY_L1_ID_TO_NAME = {k: v['name'] for k, v in CATEGORIES.items()}
CATEGORY_L2_ID_TO_NAME = {}
for k, v in CATEGORIES.items():
    CATEGORY_L2_ID_TO_NAME.update(v['children'])
CATEGORY_L2_NAME_TO_ID = {v: k for k, v in CATEGORY_L2_ID_TO_NAME.items()}
CATEGORY_ID_TO_NAME = {**CATEGORY_L1_ID_TO_NAME, **CATEGORY_L2_ID_TO_NAME}

# Providers
PROVIDERS = json.loads(_config['novel']['providers'])

CARD_TYPES = {
    1: 'Banner',
    2: 'Top',
    3: 'Left',
    4: 'List',
    5: 'Double',
    6: 'Grid',
    7: 'Bulletin',
    8: 'Recommend',
    9: 'OneSpecial',
    10: 'Vary',
}

CARD_GROUP_TYPES = {
    1: '精选(男)',
    2: '精选(女)',
    3: '男频',
    4: '女频',
    5: '书架(女)',
    6: '书架(男)',
}

CHANNEL_TYPE_MALE = 1
CHANNEL_TYPE_FEMALE = 2

CHANNEL_TYPES = {
    CHANNEL_TYPE_MALE: '男频',
    CHANNEL_TYPE_FEMALE: '女频',
}
