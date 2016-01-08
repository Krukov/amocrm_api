# -*- coding: utf-8 -*-

__all__ = ['AmoAuthException', 'AmoResponseException']


class AmoResponseException(Exception):

    def __init__(self, resp):
        self.resp = resp
        self.msg = self.message = '%s, %s' % (resp.status_code, resp.content)


class AmoAuthException(AmoResponseException):
    pass