# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from calendar import timegm
from copy import deepcopy

from .decorators import lazy_dict_property


__all__ = ['CustomField', 'ForeignField', 'ManyForeignField']


class _BaseField(object):
    def __init__(self, field=None):
        self.field = field

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        if instance._fields_data.get(self.field) is None:
            _data = instance._data.get(self.field)
            _data = self.on_get(_data, instance)
            instance._fields_data[self.field] = _data
        return instance._fields_data[self.field]

    def __set__(self, instance, value):
        if instance is None:
            return
        instance._fields_data[self.field] = None
        value = self.on_set(value, instance)
        instance._data[self.field] = value
        instance._changed_fields.append(self.field)

    def on_set(self, value, instance):
        return value

    def on_get(self, data, instance):
        return data


class _Field(_BaseField):
    pass


class _UneditableField(_Field):
    def __set__(self, instance, value):
        pass


class _ConstantField(_UneditableField):
    def __init__(self, field=None, value=None):
        super(_ConstantField, self).__init__(field)
        self._data = value

    def on_get(self, data, instance):
        return self._data


class _DateTimeField(_Field):
    def on_get(self, data, instance):
        if data is not None:
            return datetime.utcfromtimestamp(float(data))

    def on_set(self, value, instance):
        if isinstance(value, datetime):
            return timegm(value.utctimetuple())


class _StaticDateTimeField(_UneditableField, _DateTimeField):
    pass


class _BooleanField(_Field):
    def on_get(self, data, instance):
        data = int(data) if str(data).isdigit() else data
        return bool(data)


class _BaseForeignField(_Field):
    def __init__(self, object_type=None, field=None):
        super(_BaseForeignField, self).__init__(field)
        self.object_type = object_type


class ForeignField(_BaseForeignField):
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


class ManyForeignField(_BaseForeignField):
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


class _TagsField(_Field):
    def __init__(self, field=None, key=None):
        super(_TagsField, self).__init__(field)
        self.key = key

    def on_get(self, data, instance):
        if data:
            return data.replace(', ', ',').split(',')

    def on_set(self, value, *args):
        if value and value[0] and isinstance(value[0], dict):
            value = (item['name'] for item in value)
        return ', '.join(value)


class _TypeStatusField(_Field):
    def __init__(self, field=None, choices=None):
        super(_TypeStatusField, self).__init__(field)
        self.choices = choices

    def on_get(self, data, instance):
        if data and str(data).isdigit():
            _statuses = {item['id']: key for key, item in getattr(instance.objects, self.choices).items()}
            data = _statuses.get(data)
        return data

    def on_set(self, value, instance):
        _statuses = deepcopy(getattr(instance.objects, self.choices))
        if _statuses:
            return _statuses[value]['id']  # TODO: raise Exception


class CustomField(object):
    _field = 'custom_fields'

    def __init__(self, custom_field, enum=None):
        self.field = '%s_%s_%s' % (self._field, custom_field, enum)
        self.custom_field, self.enum = custom_field, enum

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        if instance._fields_data.get(self.field) is None:
            _data = instance._data.get(self._field)
            if _data is None:
                return
            custom_field_info = instance.objects._custom_fields[self.custom_field]
            _id = custom_field_info['id']
            _data = [item['values'] for item in _data if item['id'] == _id]
            _data = _data.pop() if _data else None

            enum = {enum: _id for _id, enum in custom_field_info.get('enums', {}).items()}.get(self.enum)
            _data = [item for item in _data if item.get('enum') == enum]
            self._check_field(instance)
            instance._fields_data[self.field] = _data.pop()['value'] if _data else None

        return instance._fields_data[self.field]

    def __set__(self, instance, value):
        if instance is None:
            return
        self._check_field(instance)
        instance._fields_data[self.field] = None
        custom_field_info = instance.objects._custom_fields[self.custom_field]
        _id = custom_field_info['id']
        field = [_field for _field in instance._data.setdefault(self._field, []) if _field['id'] == _id]
        enum = {enum: _id for _id, enum in custom_field_info.get('enums', {}).items()}.get(self.enum)
        if field:
            field_vals = field[0]['values']
            enum_field_vals = [item for item in field_vals if item.get('enum') == enum]
            if enum_field_vals:
                enum_field_vals[0]['value'] = value
            else:
                new_elem = {'value': value}
                if self.enum:
                    new_elem['enum'] = enum
                field_vals.append(new_elem)
        else:
            full_data = {'id': _id, 'values': [{'value': value}]}
            if self.enum is not None:
                full_data['values'][0]['enum'] = enum
            instance._data[self._field].append(full_data)
        instance._changed_fields.append(self.field)

    def _check_field(self, instance):
        if self.custom_field not in instance.objects._custom_fields:
            raise Exception('%s hasn\'t field "%s"' % (instance.name, self.custom_field))
        custom_field_info = instance.objects._custom_fields[self.custom_field]
        if custom_field_info.get('enums') and self.enum is None:
            raise Exception('Custom field "%s" must have enum' % self.custom_field)
        if self.enum is not None \
                and {enum: _id for _id, enum in custom_field_info.get('enums', {}).items()}.get(self.enum) is None:
            raise Exception('There is no enum "%s" for field "%s"' % (self.enum, self.custom_field))
