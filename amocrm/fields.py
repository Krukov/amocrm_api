# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import copy
from datetime import datetime
from collections import namedtuple


class BaseField(object):
    _parent = None

    def __init__(self, field=None):
        self.field = field
        self._data = {}

    def cleaned_data(self):
        return self._data

    def set_data(self, value):
        self._data = value

    @property
    def data(self):
        return self.cleaned_data()

    @data.setter
    def data(self, value):
        self.set_data(value)


class Field(BaseField):
    pass


class ConstantField(BaseField):

    def __init__(self, field=None, value=None):
        super(ConstantField, self).__init__(field)
        self._data = value


class DateTimeField(Field):

    def cleaned_data(self):
        return datetime.fromtimestamp(super(DateTimeField, self).cleaned_data())


class BooleanField(Field):

    def cleaned_data(self):
        return bool(super(BooleanField, self).cleaned_data())


class ForeignField(Field):

    def __init__(self, field=None, keys=None, object_type=None):
        super(ForeignField, self).__init__(field)
        self.keys = keys
        self.object_type = object_type

    def cleaned_data(self):
        _id, fields = super(ForeignField, self).cleaned_data()
        obj = self.object_type.objects.get(_id)
        [setattr(obj, name, value) for name, value in fields.items()]
        return obj


class ManyMixin(object):
    pass
    # def __init__(self, field=None):
    #     self.field = field


class ManyForeignField(ManyMixin, Field):
    pass


class ManyField(ManyMixin, Field):
    pass


class ManyDictField(ManyMixin, Field):

    def __init__(self, field=None, keys=None, types=None):
        super(ManyDictField, self).__init__(field)
        self.keys = copy.copy(keys)
        self.types = types
    
    def cleaned_data(self):
        data = super(ManyDictField, self).cleaned_data()
        return data


class CustomField(Field):
    _parent = 'custom_fields'