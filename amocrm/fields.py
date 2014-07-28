# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from collections import namedtuple, OrderedDict

from .decorators import lazy_dict_property


class BaseField(object):
    _parent = None

    def __init__(self, field=None):
        self.field = field

    def __get__(self, instance, _=None):
        if instance.fields_data.get(self.field) is None:
            if self._parent:
                _data = instance.data.get(self._parent, {}).get(self.field)
            else:
                _data = instance.data.get(self.field)
            _data = self.on_get(_data, instance)
            instance.fields_data[self.field] = _data
        return instance.fields_data[self.field]

    def __set__(self, instance, value):
        instance.fields_data[self.field] = None
        value = self.on_set(value)
        if not self._parent:
            instance.data[self.field] = value
        else:
            instance.data[self._parent][self.field] = value
        instance.changed_fields.append(self.field)

    def on_set(self, value):
        return value

    def on_get(self, data, instance):
        return data


class Field(BaseField):
    pass


class UneditableField(Field):

    def __set__(self, instance, value):
        pass


class ConstantField(UneditableField):

    def __init__(self, field=None, value=None):
        super(ConstantField, self).__init__(field)
        self._data = value

    def on_get(self, data, instance):
        return self._data


class DateTimeField(Field):

    def on_get(self, data, instance):
        if data is not None:
            return datetime.fromtimestamp(float(data))


class BooleanField(Field):

    def on_get(self, data, instance):
        data = int(data) if str(data).isdigit() else data
        return bool(data)


class BaseForeignField(Field):

    def __init__(self, object_type=None, field=None):
        super(BaseForeignField, self).__init__(field)
        self.object_type = object_type


class ForeignField(BaseForeignField):

    def __init__(self, object_type=None, field=None, auto_created=False,
                 links={}):
        super(ForeignField, self).__init__(object_type, field)
        self.auto, self.links = auto_created, links

    def on_get(self, data, instance):
        wrap = lambda this: this.get(data)
        obj = lazy_dict_property(wrap).__get__(self.object_type.objects)
        [setattr(obj, name, instance.data.get(value))
            for name, value in self.links.items()]
        return obj


class ManyForeignField(BaseForeignField):

    def __init__(self, objects_type=None, field=None, key=None):
        super(ManyForeignField, self).__init__(field=field,
                                               object_type=objects_type)
        self.key = key

    def on_get(self, data, instance):
        if data is None:
            return
        if not instance._loaded:
            return data
        items = []
        for item in data:
            wrap = lambda this: this.get(item)
            item = lazy_dict_property(wrap).__get__(self.object_type.objects)
            items.append(item)
        return items


class CommaSepField(Field):

    def __init__(self, field=None, key=None):
        super(CommaSepField, self).__init__(field)
        self.key = key

    def on_get(self, data, instance):
        if isinstance(data, basestring):
            return data
        items = []
        for item in data:
            if isinstance(item, basestring):
                items.append(item)
            elif isinstance(item, dict):
                items.append(item[self.key])
        return ', '.join(items)

    def on_set(self, value):
        return value.split(', ')


class CustomField(Field):
    _parent = 'custom_fields'
