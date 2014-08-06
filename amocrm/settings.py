# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

__all__ = ['settings']


class Settings(object):

    def __init__(self):
        self.user_login, self.user_hash, self.domain = None, None, None
        self.responsible_user = None

    def set(self, user_login, user_hash, domain, responsible_user=None):
        self.user_login, self.user_hash, self.domain = user_login, user_hash, domain
        if responsible_user is not None:
            self.responsible_user = responsible_user

    def get(self):
        return {
            'user_login': self.user_login,
            'user_hash': self.user_hash,
            'domain': self.domain,
            'responsible_user': self.responsible_user
        }

settings = Settings()
