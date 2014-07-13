# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Settings(object):

    def __init__(self):
        self.user_login, self.user_hash, self.domain = None, None, None
        self.responsible_user = None
        self.query_field = 'email'

    def set(self, user_login, user_hash, domain, responsible_user=None, query_field=None):
        self.user_login, self.user_hash, self.domain = user_login, user_hash, domain
        if responsible_user is not None:
            self.responsible_user = responsible_user
        if query_field is not None:
            self.query_field = query_field

    def get(self):
        return {
            'user_login': self.user_login,
            'user_hash': self.user_hash,
            'domain': self.domain,
            'responsible_user': self.responsible_user,
            'query_field': self.query_field,
        }

settings = Settings()