# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from datetime import datetime
from calendar import timegm
from copy import deepcopy

import six
from .utils import User
from .exceptions import UneditableFieldError

__all__ = ['CustomField', u'EnumCustomField', 'ForeignField', 'ManyForeignField']

logger = logging.getLogger('amocrm')
CHOICE_TYPE = '4'
MULTI_LIST_TYPE = '5'


class _BaseField(object):
    def __init__(self, field=None, required=False):
        self.field = field
        self.required = required

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
        if self.field not in instance._data or instance._data[self.field] != value:
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
        raise UneditableFieldError


class _ConstantField(_UneditableField):
    def __init__(self, field=None, value=None):
        super(_ConstantField, self).__init__(field, True)
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
    def __init__(self, object_type=None, field=None, required=False):
        super(_BaseForeignField, self).__init__(field, required=required)
        self.object_type = object_type


class ForeignField(_BaseForeignField):
    def __init__(self, object_type=None, field=None, auto_created=False,
                 links={}, required=False):
        super(ForeignField, self).__init__(object_type, field, required=required)
        self.auto, self.links = auto_created, deepcopy(links)
        self.links['id'] = field

    def on_get(self, data, instance):
        obj = self.object_type()
        obj._fields_data['id'] = instance._data.get(self.field)
        obj._data = {name: instance._data.get(value)
                     for name, value in self.links.items()}
        return obj

    def on_set(self, val, instance):
        if isinstance(instance._get_field_by_name(self.field), self.__class__):
            instance._fields_data[self.field] = val
            return val.id
        elif str(val).isdigit():
            return int(val)


class ManyForeignField(_BaseForeignField):
    def __init__(self, objects_type=None, field=None, key=None, required=False):
        super(ManyForeignField, self).__init__(field=field,
                                               object_type=objects_type,
                                               required=required)
        self.key = key

    def on_get(self, data, instance):
        if not data:
            return []
        if not instance._loaded:
            return data
        if isinstance(data, (list, tuple)):
            return [self.object_type().objects.get(item) for item in data]
        return self.object_type().objects.get(data)

    def on_set(self, value, instance):
        if value is None:
            instance._fields_data[self.field] = []
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        instance._fields_data[self.field] = [item for item in value]
        return [int(item) if isinstance(item, (str, int)) else int(item.id) for item in value]


class _TagsField(_Field):
    def __init__(self, field=None, key=None, required=False):
        super(_TagsField, self).__init__(field, required=required)
        self.key = key

    def on_get(self, data, instance):
        if data:
            if isinstance(data, (list, tuple)):
                return [item['name'] for item in data]
            return data.replace(', ', ',').split(',')

    def on_set(self, value, *args):
        if value and value[0] and isinstance(value[0], dict):
            value = (item['name'] for item in value)
        return ', '.join(value)


class _TypeField(_Field):
    def __init__(self, field=None, choices=None, required=False):
        super(_TypeField, self).__init__(field, required=required)
        self.choices = choices

    def on_get(self, data, instance):
        if data:
            _data = [key for key, item in self.get_choices(instance).items()
                     if six.text_type(item['id']) == six.text_type(data)
                     or six.text_type(item.get('code', '')) == six.text_type(data)]
            data = _data.pop()
        return data

    def on_set(self, value, instance):
        return self.get_choices(instance)[value]['id']

    def get_choices(self, instance):
        return getattr(instance.objects, self.choices)


class _StatusTypeField(_TypeField):

    def __init__(self, **kwargs):
        super(_StatusTypeField, self).__init__('status_id', choices='leads_statuses', **kwargs)

    def get_choices(self, instance):
        ch = super(_StatusTypeField, self).get_choices(instance)
        ch.update(instance.statuses)
        return ch


class Owner(_Field):

    def __init__(self, field='responsible_user_id'):
        super(Owner, self).__init__(field, required=False)

    def on_get(self, data, instance):
        if data and str(data).isdigit():
            return [item for item in instance.objects.users if str(item.id) == str(data)].pop()
        return data

    def on_set(self, value, instance):
        if isinstance(value, six.string_types):
            return User.get_one(instance.objects.users, [value, ]).id
        elif value is not None:
            return value.id


class CustomField(object):
    _field = 'custom_fields'

    def __init__(self, custom_field, subtypes=False, required=False):
        self.field = '%s_%s' % (self._field, custom_field)
        self.custom_field, self.subtypes = custom_field, subtypes
        self.required = required

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        if instance._fields_data.get(self.field) is None:
            _data = instance._data.get(self._field)

            if _data is None:
                return
            self._check_field(instance)
            custom_field_info = instance.objects._custom_fields[self.custom_field]
            _id = custom_field_info['id']
            _data = list(_data.values()) if isinstance(_data, dict) else _data
            _data = [item['values'] for item in _data if item['id'] == _id]

            _data = _data[-1] if _data else None
            _data = list(_data.values()) if isinstance(_data, dict) else _data
            if custom_field_info['type_id'] == MULTI_LIST_TYPE and _data and not isinstance(_data[0], dict):
                _data = [{'value': item[1]} for item in custom_field_info['enums'].items()
                         if item[0] in _data]
            _data = [item['value'] for item in _data] if _data else None
            if custom_field_info['type_id'] != MULTI_LIST_TYPE and custom_field_info.get(u'multiple') != u'Y' and _data:
                _data = _data.pop()

            if _data in ['0', '1']:
                _data = bool(int(_data))

            instance._fields_data[self.field] = _data
        return instance._fields_data[self.field]

    def __set__(self, instance, value):
        if instance is None:
            return
        self._check_field(instance)
        if isinstance(value, bool):
            value = str(int(value))
        instance._fields_data[self.field] = None
        custom_field_info = instance.objects._custom_fields[self.custom_field]
        _id = custom_field_info['id']
        instance._data[self._field] = instance._data.get(self._field, None) or []
        fields = [item for item in instance._data[self._field] if item['id'] == _id]

        if isinstance(value, (list, tuple)):
            _elems = []
            for v in value:
                _elems.append({'value': v})
        else:
            _elems = [{'value': value}]

        if 'enums' in custom_field_info and custom_field_info['enums']:
            values = [item['value'] for item in _elems]
            _elems = [{'enum': item[0], 'value': item[1]} for item in custom_field_info['enums'].items()
                      if item[1] in values]
            if custom_field_info['type_id'] == MULTI_LIST_TYPE:
                _elems = [item[0] for item in custom_field_info['enums'].items()
                          if item[1] in values]

            if not _elems:
                raise ValueError('Invalid value for %s' % self.field)

        if not fields:
            full_data = {'id': _id, 'values': _elems, 'name': self.custom_field}
            if self.subtypes:
                full_data['values'] = [{'subtype': str(i),
                                        'value': val.strip()} for i, val in enumerate(value.split(';'), start=1)]
            instance._data[self._field].append(full_data)
        else:
            fields[0]['values'] = _elems
        if self._field not in instance._changed_fields:
            instance._changed_fields.append(self._field)

    def _check_field(self, instance):
        if self.custom_field not in instance.objects._custom_fields:
            raise ValueError('%s hasn\'t field "%s"' % (instance, self.custom_field))


class EnumCustomField(CustomField):

    def __init__(self, custom_field, enum):
        super(EnumCustomField, self).__init__(custom_field)
        self.field = self.field + enum
        self.enum = enum

    def __get__(self, instance, _=None):
        if instance is None:
            return self
        if instance._fields_data.get(self.field) is None:
            _data = instance._data.get(self._field)

            if _data is None:
                return
            if self.custom_field not in instance.objects._custom_fields:
                raise ValueError(u"%s have not custom field '%s'" % (instance.objects.name, self.custom_field))
            custom_field_info = instance.objects._custom_fields[self.custom_field]
            _id = custom_field_info['id']
            _data = [item['values'] for item in _data if item['id'] == _id]

            _data = _data[-1] if _data else None
            enum = {enum_name: _id for _id, enum_name in custom_field_info.get('enums', {}).items()}.get(self.enum)
            if not enum:
                raise ValueError(u"%s have not custom field '%s' with enum %s" % (instance.objects.name,
                                                                                  self.custom_field,
                                                                                  self.enum))

            if _data is None:
                return
            _data = [item for item in _data if item.get('enum') == enum]
            self._check_field(instance)
            instance._fields_data[self.field] = [item['value'] for item in _data] if _data else None
            if len(_data) == 1:
                instance._fields_data[self.field] = instance._fields_data[self.field].pop()

        return instance._fields_data[self.field]

    def __set__(self, instance, values):
        if instance is None:
            return
        if not isinstance(values, (list, tuple)):
            values = [values]
        self._check_field(instance)
        instance._fields_data[self.field] = None
        custom_field_info = instance.objects._custom_fields[self.custom_field]
        _id = custom_field_info['id']
        field = [_field for _field in instance._data.setdefault(self._field, []) if _field['id'] == _id]
        enum = {enum: _id for _id, enum in custom_field_info.get('enums', {}).items()}.get(self.enum)
        if field:
            field[0]['values'] = [{'value': value, 'enum': enum} for value in values]
        else:
            full_data = {'id': _id, 'values': [{'value': value, 'enum': enum} for value in values]}
            instance._data[self._field].append(full_data)
        if self._field not in instance._changed_fields:
            instance._changed_fields.append(self._field)

    def _check_field(self, instance):
        super(EnumCustomField, self)._check_field(instance)
        custom_field_info = instance.objects._custom_fields[self.custom_field]
        if {enum: _id for _id, enum in custom_field_info.get('enums', {}).items()}.get(self.enum) is None:
            raise Exception('There is no enum "%s" for a field "%s"' % (self.enum, self.custom_field))