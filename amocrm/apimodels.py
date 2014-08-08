# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import time
import six

from . import fields
from .api import *


__all__ = ['BaseCompany', 'BaseContact', 'ContactTask', 'LeadTask', 'BaseLead']


class _ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('_fields', {})
        [attrs.update(getattr(base, '_fields', {})) for base in bases]
        attrs['_fields'].update({name: instance for name, instance in attrs.items()
                                 if isinstance(instance, fields._BaseField)})
        super_new = super(_ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super(_ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        return super_new


class _BaseModel(six.with_metaclass(_ModelMeta)):
    _fields = {}

    _ELEMENT_TYPES = {
        'contact': 1,
        'lead': 2,
    }

    id = fields.UneditableField('id')
    date_create = fields.DateTimeField('date_create')
    last_modified = fields.DateTimeField('last_modified')
    request = fields.Field('request_id')

    def __init__(self, data=None, **kwargs):
        self._data, self._init_data = {}, {}
        self._fields_data, self._changed_fields = {}, []
        self._loaded = bool(kwargs.pop('_loaded', False))
        if self._loaded:
            self._data = data or kwargs
        else:
            self._init_data = data or kwargs
        if not self._loaded:
            for name, field in self._fields.items():
                value = self._init_data.get(name, None)
                if value is None:
                    continue
                if isinstance(field, fields.ForeignField) and name in self._init_data:
                    main_field = field.object_type.objects._main_field
                    if isinstance(value, field.object_type):
                        setattr(self, name, value)
                    elif main_field in field.links.keys():
                        self._data[field.links[main_field]] = self._init_data[name]
                        self._changed_fields.append(field.field)
                else:
                    if isinstance(field, fields.UneditableField):
                        self._data[field.field] = value
                    setattr(self, name, value)
                    self._changed_fields.append(field.field)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __getattribute__(self, name):
        value = super(_BaseModel, self).__getattribute__(name)
        if (value is None and not self._loaded and name != 'id' and self.id is not None
                and self._fields[name].field not in self._changed_fields):
            self.__init__(self.objects.get(self.id)._data)  # trying to get info from crm
        return value or super(_BaseModel, self).__getattribute__(name)

    def _save_fk(self):
        for name, field in self._fields.items():
            if not isinstance(field, fields.ForeignField):
                continue
            main_field = field.object_type.objects._main_field
            if main_field is not None:
                value = getattr(getattr(self, name), main_field)
                self._data[field.links[main_field]] = value
            if getattr(field, 'auto', None):
                continue
            if (field.field in self._changed_fields or not self._loaded) \
                    and (name in self._data or name in self._init_data):
                getattr(self, name).save()
                self._data[field.field] = getattr(self, name).id

    def save(self, update_if_exists=True):
        self._save_fk()
        if self.date_create is None:
            self.date_create = time.time()
        self.last_modified = time.time()
        if self.id is not None:
            method = self.objects.update
        elif update_if_exists:
            method = self.objects.create_or_update
        else:
            method = self.objects.create
        result = method(**{k: v for k, v in self._data.items()})
        self._data['id'] = result

    def _get_field_by_name(self, name):
        result = [v for k, v in self._fields.items() if v.field == name]
        return result.pop()


class _AbstractaNamedModel(_BaseModel):
    name = fields.Field('name')
    linked_leads = fields.ManyForeignField('linked_leads_id')
    tags = fields.TagsField('tags', 'name')
    rui = fields.Field('responsible_user_id')


class BaseCompany(_AbstractaNamedModel):
    type = fields.ConstantField('type', 'company')

    objects = CompanyManager()


class BaseLead(_AbstractaNamedModel):
    status = fields.StatusField('status_id', choices='leads_statuses')
    price = fields.Field('price')

    objects = LeadsManager()


class BaseContact(_AbstractaNamedModel):
    type = fields.ConstantField('type', 'contact')
    company = fields.ForeignField(BaseCompany, 'linked_company_id',
                                  auto_created=False,
                                  links={'name': 'company_name'})
    created_user = fields.UneditableField('created_user')

    objects = ContactsManager()

    def create_task(self, text, task_type=None, complete_till=None):
        task = ContactTask(contact=self, type=task_type, text=text, complete_till=complete_till)
        task.save()
        return task


class _AbstractTaskModel(_BaseModel):
    type = fields.StatusField('task_type', 'task_types')
    text = fields.Field('text')
    complete_till = fields.DateTimeField('complete_till')


class LeadTask(_AbstractTaskModel):
    lead = fields.ForeignField(BaseLead, 'element_id')
    _element_type = fields.ConstantField('element_type',
                                         _BaseModel._ELEMENT_TYPES['lead'])

    objects = TasksManager()


class ContactTask(_AbstractTaskModel):
    contact = fields.ForeignField(BaseContact, 'element_id')
    _element_type = fields.ConstantField('element_type',
                                         _BaseModel._ELEMENT_TYPES['contact'])

    objects = TasksManager()
