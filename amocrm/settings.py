# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os.path
from configparser import RawConfigParser

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

    def set_from_config(self, path=['amocrm.ini', '~/amocrm.ini']):
        if isinstance(path, str):
            path = [path]

        for config in map(os.path.expanduser, path):
            if os.path.exists(config):
                parser = RawConfigParser()
                parser.read_string('[_default_section]\n' + open(config).read())
                section = 'amocrm' if 'amocrm' in parser else '_default_section'
                self.set(
                    parser[section]['user_login'],
                    parser[section]['user_hash'],
                    parser[section]['domain'],
                    parser[section].get('responsible_user')
                )


settings = Settings()
