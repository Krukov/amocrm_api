# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import time

import six
if six.PY2:
    from urlparse import urlparse, parse_qsl
else:
    from urllib.parse import urlparse, parse_qsl

from responses import RequestsMock

from amoapi.base import BaseAmoManager


class FakeApi(object):
    """docstring for FakeApi"""
    def __init__(self):
        self.login, self.hash = None, None
        super(FakeApi, self).__init__()

    def reset(self):
        super(FakeApi, self).reset()
        self._data = json.loads(open('generated.json').read())

    def _auth(self, obj, params):
        r = {'auth': False}
        if 'USER_LOGIN' in params and 'USER_HASH' in params:
            if params['USER_LOGIN'] == self.login \
                            and params['USER_HASH'] == self.hash:
                r['auth'] = True
        return json.dumps(r)

    def _list(self, obj, params):
        params = params.get('request', {}).get(obj)
        _id, query = params.get('id'), params.get('query')
        resp = []
        if _id:
            resp = [i for i in self.data[obj] if i['id'] == _id]
        elif query:
            resp = [i for i in self.data[obj] if query in i.items()]
        if 'limit_rows' in params:
            resp = resp[int(params.get('limit_offset', 0)),
                        int(params.get('limit_rows'))]
        return json.dumps({'response': {obj: resp}})

    def _set(self, obj, params):
        resp = {}
        params = params.get('request', {}).get(obj)
        if params:
            if 'update' in params:
                params['update']['last_modified'] = time.time()
                target_id = params['update']['id']
                update_obj = (i for i in self.data
                        if i['id'] == target_id).next()
                update_obj.update(params['update'])
                resp = {'update': {'id': target_id}}
            elif 'add' in params:
                params['add']['last_modified'] = time.time()
                _id = max(self.data[obj], lambda x: x['id'])['id'] + 1
                params['add']['id'] = _id
                self.data[obj].append(params['add'])
                resp = {'add': {'id': _id, 'request_id': 1}}
        return json.dumps({'response': {obj: resp}})

    def _current(self, obj, params):
        return json.dumps(self.data[obj])


class AmoApiMock(RequestsMock):
    _urls_data = BaseAmoManager._methods
    _objects = ('contacts', 'notes', 'company', 'tasks', 'leads')
    _base_url = 'https://%(domain)s.amocrm.ru' + BaseAmoManager._base_path
    _format = BaseAmoManager.format_

    def __init__(self):
        super(AmoApiMock, self).__init__()
        self._faker = FakeApi()

    def _find_match(self, request):
        result = super(AmoApiMock, self)._find_match(request)
        if not result:
            result = self._get_response(request)
        return result

    def _get_response(self, request):
        url_parsed = urlparse(request.url)
        url_qsl = parse_qsl(url_parsed.query)
        obj, method = url_parsed.path.split('/')[-2:]
        method = method.split('.')[0]
        return getattr(self._faker, '_%s' % method)(obj, url_qsl)

    def set_login_params(self, login, hash):
        self._faker.login = login
        self._faker.hash = hash

amomock = AmoApiMock()
