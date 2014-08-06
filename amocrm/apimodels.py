# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import time

from . import fields
from .api import *


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs.setdefault('_fields', {})
        [attrs.update(getattr(base, '_fields', {})) for base in bases]
        attrs['_fields'].update({name: instance for name, instance in attrs.items()
                            if isinstance(instance, fields.BaseField)})
        super_new = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        return super_new


class BaseModel(object):
    __metaclass__ = ModelMeta

    _fields = {}

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
                val = self._init_data.get(name, None)
                if isinstance(field, fields.ForeignField) and name in self._init_data:
                    mf = field.object_type.objects._main_field
                    if isinstance(self._init_data[name], field.object_type):
                        pass
                    elif mf in field.links.keys():
                        self._data[field.links[mf]] = self._init_data[name]
                        self._changed_fields.append(field.field)
                else:
                    if val is not None:
                        self._data[field.field] = val
                        self._changed_fields.append(field.field)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def _save_fk(self):
        for name, field in self._fields.items():
            if not isinstance(field, fields.ForeignField):
                continue
            mf = field.object_type.objects._main_field
            value = getattr(getattr(self, name), mf)
            self._data[field.links[mf]] = value
            if getattr(field, 'auto', None):
                continue
            if (field.field in self._changed_fields or not self._loaded)\
                    and (name in self._data or name in self._init_data):
                if getattr(self, name).id is not None:
                    result = field.object_type.objects.update(
                        **{mf: value, 'id': getattr(self, name).id}
                    )
                else:
                    result = field.object_type.objects.create_or_update(
                        **{mf: value}
                    )
                self._data[field.field] = result
                setattr(getattr(self, name), 'id', result)

    def save(self, update_if_exists=True):
        self._save_fk()
        if self.date_create is None:
            self.date_create = time.time()
        self.last_modified = time.time()
        _send_data = {k: v for k, v in self._data.items()}
        if self.id is not None:
            method = self.objects.update
        elif update_if_exists:
            method = self.objects.create_or_update
        else:
            method = self.objects.create
        result = method(**_send_data)
        self._data['id'] = result

    def _get_field_by_name(self, name):
        result = [v for k, v in self._fields.items() if v.field == name]
        return result.pop()

    id = fields.UneditableField('id')
    name = fields.Field('name')
    linked_leads = fields.ManyForeignField('linked_leads_id')
    date_create = fields.DateTimeField('date_create')
    last_modified = fields.DateTimeField('last_modified')
    tags = fields.CommaSepField('tags', 'name')
    rui = fields.Field('responsible_user_id')
    deleted = fields.BooleanField('deleted')


class Company(BaseModel):

    type = fields.ConstantField('type', 'company')

    objects = CompanyManager()


class Lead(BaseModel):

    status = fields.Field('status_id')  # TODO: status field
    price = fields.Field('price')

    objects = LeadsManager()

class _BaseTask(BaseModel):
    ELEMENT_TYPES = {
        'contact': 1,
        'lead': 2,
    }

    type = fields.Field('task_type')
    text = fields.Field('text')
    complete_till = fields.DateTimeField('complete_till')

    objects = TasksManager()

class LeadTask(_BaseTask):

    lead = fields.ForeignField(Lead, 'element_id')
    _element_type = fields.ConstantField('element_type',
                                         _BaseTask.ELEMENT_TYPES['lead'])


class Contact(BaseModel):

    type = fields.ConstantField('type', 'contact')
    company = fields.ForeignField(Company, 'linked_company_id',
                                  auto_created=False,
                                  links={'name': 'company_name'})
    created_user = fields.Field('created_user')

    objects = ContactsManager()

    def create_task(self, text, task_type=None, complete_till=None):
        task = ContactTask(contact=self, type=task_type , text=text, complete_till=complete_till)
        task.save()
        return task

class ContactTask(_BaseTask):

    contact = fields.ForeignField(Contact, 'element_id')
    _element_type = fields.ConstantField('element_type',
                                         _BaseTask.ELEMENT_TYPES['contact'])
    