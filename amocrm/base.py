# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import json
from abc import *
from collections import defaultdict
from time import time
from copy import copy, deepcopy

import requests

from .decorators import amo_request, lazy_dict_property
from .logger import logger

AMO_LOGIN_PATH = '/private/api/auth.php'
REQUEST_PARAMS = {
    'headers': {'User-Agent': 'Amocrm API module. Python powered'},
    'timeout': 3,
}

tree = lambda: defaultdict(tree)


class BaseAmoManager(object):
    __metaclass__ = ABCMeta

    methods = {}
    format_ = 'json'

    object_type = None
    _base_path = '/private/api/v2/%(format)s%(name)s%(path)s'
    _methods = {
        'account_info': {'path': 'current', 'result': ['account'], 'name': 'accounts'},
        'list': {'path': 'list', 'result': True},
        'add': {'path': 'set', 'method': 'post', 'result': ['add', 0, 'id'], 'container': ['add']},
        'update': {'path': 'set', 'method': 'post', 'container': ['update'], 'timestamp': True},
    }

    def __init__(self, user_login, user_hash, domain, responsible_user=None, query_field='email'):
        self._domain = domain
        self._login_data = {'USER_LOGIN': user_login, 'USER_HASH': user_hash, 'type': 'json'}
        self._responsible_user = responsible_user or user_login
        self._query_field = query_field

        self.methods = deepcopy(self.methods)
        self.methods.update(self._methods)

    @abstractproperty
    def name(cls):
        pass

    @lazy_dict_property
    def custom_fields(self):
        return self.get_custom_fields(to=self.name)

    @lazy_dict_property
    def account_info(self):
        return self.get_account_info()

    @lazy_dict_property
    def rui(self):
        if isinstance(self._responsible_user, int):
            return self._responsible_user
        else:
            filter_func = lambda _: _.get('login') == self._responsible_user or \
                                    _.get('name') == self._responsible_user
            user = filter(filter_func, self.account_info.get('users', [])).pop()
            if not user:
                raise Exception(u'Can not get responsible user id')
            return user.get('id')

    def _request(self, path, method, data):
        params = copy(self._login_data)
        if method != 'POST':
            params.update(data)
            data = None

        logger.info('Sending %s request to %s' % (method, path))
        logger.debug('Data: %s \n Params: %s' % (data, params))

        req = getattr(requests, method.lower(), 'get')(self.url(path), data=json.dumps(data), params=params)
        if not req.ok:
            logger.error('Something went wrong')
            return req.raise_for_status()
        try:
            return req.json()
        except ValueError:
            return req.content

    def _create_container(self, container, data):
        container = ['request', self.name] + container
        _container = _ = tree()
        for i, elem in enumerate(container):
            if i + 1 == len(container):
                _[elem] = data
                continue
            _ = _[elem]
        return _container

    def _modify_response(self, response, result):
        if isinstance(result, (list, tuple)):
            result = ['response', self.name] + result
            try:
                for key in result:
                    response = response[key]
            except (TypeError, KeyError):
                pass
        elif result:
            try:
                response = response['response'][self.name]
            except (TypeError, KeyError):
                pass
        return response

    def request(self, method, data=None):
        path = self.get_path(method)
        method = self.methods[method]
        method_type = method.get('method', 'get')
        timestamp, container, result = method.get('timestamp'), method.get('container'), method.get('result')

        if timestamp:
            _time = timestamp if isinstance(timestamp, (str, unicode)) else 'last_modified'
            data.setdafault(_time, int(time()))
        if container is not None:
            data = self._create_container(container, data)
        response = self._request(path=path, method=method_type, data=data)
        return self._modify_response(response, result)

    def get_path(self, method_name):
        name = self.methods[method_name].get('name', self.name)
        path = self.methods[method_name]['path']
        if not name.startswith('/'):
            name = '/' + name
        if not name.endswith('/') and not path.startswith('/'):
            name += '/'
        return self._base_path % {'path': path, 'format': self.format_, 'name': name}

    def url(self, path):
        return 'https://%(domain)s.amocrm.ru%(path)s' % {'domain': self._domain, 'path': path}

    def get_custom_fields(self, to):
        custom_fields = self.account_info['custom_fields'][to]
        return {field['name']: field.get('id') for field in custom_fields}

    @amo_request(method='account_info')
    def get_account_info(self):
        return {}

    @amo_request(method='list')
    def get_list(self, limit=100, limit_offset=None, query=None):
        request = query or {}
        if limit is not None:
            request['limit_rows'] = limit
        if limit_offset is not None:
            request['limit_offset'] = limit_offset
        return request

    def get(self, id_):
        return self.get_list(limit=1, query={'id': id_, 'type': self.name[:-1]}).pop()

    def search(self, query):
        if not isinstance(query, dict):
            query = {self._query_field: query}
        query = {'type': self.object_type or self.name[:-1], 'query': query}
        return self.get_list(limit=5, query=query)

    @amo_request('add')
    def add(self, **kwargs):
        return self.add_data(**kwargs)

    @amo_request('update')
    def update(self, **kwargs):
        return self.update_data(**kwargs)

    def create_or_update(self, **kwargs):
        return self.create_or_update_data(**kwargs)

    @abstractmethod
    def add_data(self, **kwargs):
        return kwargs

    @abstractmethod
    def update_data(self, **kwargs):
        return kwargs

    @abstractmethod
    def create_or_update_data(self, **kwargs):
        query = kwargs.get(self._query_field)
        contact = self.search(query) if query else {}
        data = self.merge_data(kwargs, contact)
        if contact:
            data['id'] = contact['id']
            return self.update(**data)
        else:
            return self.add(**data)

    @staticmethod
    def merge_data(new, old):
        return new


class BlankMixin(object):

    def add_data(self, **kwargs):
        return super(BlankMixin, self).add_data(**kwargs)

    def update_data(self, **kwargs):
        return super(BlankMixin, self).update_data(**kwargs)

    def create_or_update_data(self, **kwargs):
        return super(BlankMixin, self).create_or_update_data(**kwargs)


class Field(object):
    _parent = ''

    def __init__(self, name=None):
        self.name = name


class CustomField(Field):
    _parent = 'custom_fields'


def Helper(_class, name):

    class Mixin(object):
        def __init__(self, *args, **kwargs):
            super(Mixin, self).__init__(*args, **kwargs)
            setattr(self, name, _class(*args, **kwargs))
            setattr(getattr(self, name), '_account_info', self.account_info)
    return Mixin