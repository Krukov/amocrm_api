# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from collections import namedtuple, OrderedDict

from .decorators import lazy_dict_property


class BaseField(object):
    _parent = None

    def __init__(self, field=None):
        self.field = field
        self.refresh()

    def __get__(self, instance, _=None):
        if instance.fields_data.get(self.field) is None:
            self._instance = instance
            if self._parent:
                self.data = instance.data.get(self._parent, {}).get(self.field)
            else:
                self.data = instance.data.get(self.field)
            if hasattr(self, 'keys_map'):
                self._keys_data = {key: instance.data.get(val)
                                   for key, val in self.keys_map.items()}
            instance.fields_data[self.field] = self.data
            self.refresh()
        return instance.fields_data[self.field]

    def __set__(self, instance, value):
        if not self._parent:
            instance.data[self.field] = value
        else:
            instance.data[self._parent][self.field] = value
        instance.changed_fields.append(self.field)

    def refresh(self):
        self._data, self._instance = None, None

    def cleaned_data(self):
        return self._data

    def set_data(self, value):
        self._data = value
        return self

    @property
    def data(self):
        return self.cleaned_data()

    @data.setter
    def data(self, value):
        self.set_data(value)


class Field(BaseField):
    pass


class UneditableField(Field):

    def __set__(self, instance, value):
        pass


class ConstantField(UneditableField):

    def __init__(self, field=None, value=None):
        super(ConstantField, self).__init__(field)
        self._data = value


class DateTimeField(Field):

    def cleaned_data(self):
        data = super(DateTimeField, self).cleaned_data()
        if data is not None:
            return datetime.fromtimestamp(float(data))


class BooleanField(Field):

    def cleaned_data(self):
        data = super(BooleanField, self).cleaned_data()
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

    def cleaned_data(self):
        _id = super(ForeignField, self).cleaned_data()
        wrap = lambda this: this.get(_id)
        obj = lazy_dict_property(wrap).__get__(self.object_type.objects)
        [setattr(obj, name, self._instance.data.get(value))
            for name, value in self.links.items()]

        return obj


class ManyForeignField(BaseForeignField):

    def __init__(self, objects_type=None, field=None, key=None):
        super(ManyForeignField, self).__init__(field=field,
                                               object_type=objects_type)
        self.key = key

    def cleaned_data(self):
        data = super(ManyForeignField, self).cleaned_data()
        if data is None:
            return
        if not self._instance._loaded:
            return data
        items = []
        for item in data:
            wrap = lambda this: this.get(item)
            item = lazy_dict_property(wrap).__get__(self.object_type.objects)
            items.append(item)
        return items


class ManyDictField(Field):

    def __init__(self, field=None, key=None):
        super(ManyDictField, self).__init__(field)
        self.key = key

    def cleaned_data(self):
        data = super(ManyDictField, self).cleaned_data()
        items = {}
        for item in data:
            item = OrderedDict(item)
            _item = namedtuple('item', item.keys())
            items[item[self.key]] = _item(**item)
        return items


class CustomField(Field):
    _parent = 'custom_fields'
