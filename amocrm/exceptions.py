# -*- coding: utf-8 -*-

__all__ = ['AmoAuthException', 'AmoResponseException', 'ObjectNotFound', 'UneditableFieldError']


class AmoApiException(Exception):
    pass


class ObjectNotFound(AmoApiException):
    pass


class AmoResponseException(AmoApiException):

    def __init__(self, resp):
        self.resp = resp
        self.msg = self.message = '%s, %s' % (resp.status_code, resp.content)


class AmoAuthException(AmoResponseException):
    pass


class UneditableFieldError(AmoApiException):
    pass