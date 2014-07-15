# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from responses import RequestsMock

from amoapi.base import BaseAmoManager


class AmoApiMock(RequestsMock):
    _urls_data = BaseAmoManager._methods
    _objects = ('contacts', 'notes', 'company', 'tasks', 'leads')
    _base_url = 'https://%(domain)s.amocrm.ru' + BaseAmoManager._base_path
    _format = BaseAmoManager.format_

    def __init__(self, domain='test'):
        super(AmoApiMock, self).__init__()
        self.domain = domain
        self.init_urls()

    def init_urls(self):
        for obj in self._objects:
            for method, data in self._urls_data.iteritems():
                url = self._base_url.format(domain=self.domain, format=self._format,
                     name=obj, path=self._urls_data.get('path'))

                self.add(
                    url=url,
                    method=data.get('method', 'get').upper(),
                    content_type='application/json',
                    match_querystring='',
                    status=status,
                    body=getattr(self, 'gen_%s' % obj)() 
                })