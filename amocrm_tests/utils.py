# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
import time
from functools import wraps

import six
if six.PY2:
    from urlparse import urlparse, parse_qsl
else:
    from urllib.parse import urlparse, parse_qsl

from responses import RequestsMock


def check_auth(func):
    @wraps(func)
    def _call(self, obj, params):
        if self._check_auth(params):
            return func(self, obj, params)
        return json.dumps({'status': 'error', 'auth': False})

    return _call


class FakeApi(object):
    """docstring for FakeApi"""
    def __init__(self):
        self.login, self.hash = None, None
        self._data = json.loads(open('generated.json').read())

    def _check_auth(self, params):
        login = params.pop('USER_LOGIN', None)
        _hash = params.pop('USER_HASH', None)
        if login == self.login and _hash == self.hash:
            return True
        return False

    def _auth(self, obj, params):
        r = {'auth': False}
        if self._check_auth(params):
            r['auth'] = True
        return json.dumps(r)

    @check_auth
    def _list(self, obj, params):
        params = json.loads(params.get('request', {})).get(obj)
        if params is None:
            return json.dumps({'status': 'error'})
        _id, query = params.get('id'), params.get('query')
        resp = []
        if _id:
            resp = [i for i in self._data[obj] if i['id'] == _id]
        elif query:
            resp = [i for i in self._data[obj] if all([j in i.items() for j in query.items()])]
        else:
            resp = self._data[obj]
        if 'limit_rows' in params:
            resp = resp[int(params.get('limit_offset', 0)):int(params.get('limit_rows'))]
        return json.dumps({'response': {obj: resp}})

    @check_auth
    def _set(self, obj, params):
        resp = {}
        params = json.loads(params.get('request', {})).get(obj)
        if params:
            if 'update' in params:
                params['update']['last_modified'] = time.time()
                target_id = params['update']['id']
                update_obj = (i for i in self._data
                              if i['id'] == target_id).next()
                update_obj.update(params['update'])
                resp = {'update': {'id': target_id}}
            elif 'add' in params:
                params['add']['last_modified'] = time.time()
                max_id = max(self._data[obj], lambda x: int(x['id']))
                print max_id
                _id = int(max_id['id']) + 1
                params['add']['id'] = _id
                self._data[obj].append(params['add'])
                resp = {'add': {'id': _id, 'request_id': 1}}
        return json.dumps({'response': {obj: resp}})

    @check_auth
    def _current(self, obj, params):
        return json.dumps({'response': {obj: self._data[obj]}})


class AmoApiMock(RequestsMock):
    _objects = ('contacts', 'notes', 'company', 'tasks', 'leads')
    _base_url = 'https://%(domain)s.amocrm.ru/private/api/v2/%(format)s%(name)s%(path)s'
    _format = 'json'

    def reset(self):
        super(AmoApiMock, self).reset()
        self._faker = FakeApi()

    def _find_match(self, request):
        result = super(AmoApiMock, self)._find_match(request)
        if not result:
            result = self._get_response(request)
        return result

    def _get_response(self, request):
        url_parsed = urlparse(request.url)
        if url_parsed.query or request.body:
            url_qsl = dict(parse_qsl(url_parsed.query) + parse_qsl(request.body))
        else:
            url_qsl = {}
        obj, method = url_parsed.path.split('/')[-2:]
        method = method.split('.')[0]
        body = getattr(self._faker, '_%s' % method)(obj, url_qsl)
        return {
            'body': body,
            'content_type': 'text/plain',
            'status': 200,
            'adding_headers': None,
            'stream': False
        }

    def set_login_params(self, login, _hash):
        self._faker.login = login
        self._faker.hash = _hash


amomock = AmoApiMock()
