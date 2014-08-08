# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from copy import deepcopy

from .decorators import lazy_dict_property


class _BaseField(object):
    _parent = None

    def __init__(self, field=None):
        self.field = field

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        if instance._fields_data.get(self.field) is None:
            if self._parent:
                _data = instance._data.get(self._parent, {}).get(self.field)
            else:
                _data = instance._data.get(self.field)
            _data = self.on_get(_data, instance)
            instance._fields_data[self.field] = _data
        return instance._fields_data[self.field]

    def __set__(self, instance, value):
        if instance is None:
            return
        instance._fields_data[self.field] = None
        value = self.on_set(value, instance)
        if not self._parent:
            instance._data[self.field] = value
        else:
            instance._data[self._parent][self.field] = value
        instance._changed_fields.append(self.field)

    def on_set(self, value, instance):
        return value

    def on_get(self, data, instance):
        return data


class Field(_BaseField):
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
        self.auto, self.links = auto_created, deepcopy(links)
        self.links['id'] = field

    def on_get(self, data, instance):
        obj = self.object_type()
        obj._fields_data['id'] = instance._data.get(self.field)
        [setattr(obj, name, instance._data.get(value))
            for name, value in self.links.items()]
        return obj

    def on_set(self, val, instance):
        if isinstance(instance._get_field_by_name(self.field), self.__class__):
            instance._fields_data[self.field] = val
            return val.id
        elif str(val).isdigit():
            return int(val)


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


class TagsField(Field):

    def __init__(self, field=None, key=None):
        super(TagsField, self).__init__(field)
        self.key = key

    def on_get(self, data, instance):
        return data.replace(', ', ',').split(',')

    def on_set(self, value, *args):
        if value and value[0] and isinstance(value[0], dict):
            value = (item['name'] for item in value)
        return ', '.join(value)


class CustomField(Field):
    _parent = 'custom_fields'


class TypeStatusField(Field):

    def __init__(self, field=None, choices=None):
        super(TypeStatusField, self).__init__(field)
        self.choices = choices

    def on_get(self, data, instance):
        if data and str(data).isdigit():
            _statuses = {item['id']: item for item in deepcopy(getattr(instance.objects, self.choices))}
            data = _statuses.get(data)['name']
        return data

    def on_set(self, value, instance):
        _statuses = deepcopy(getattr(instance.objects, self.choices))
        if _statuses:
            _statuses = {item.pop('name'): item for item in _statuses}
            return _statuses[value]['id'] # TODO: raise Exception
