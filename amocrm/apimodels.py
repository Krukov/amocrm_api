# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from copy import deepcopy
from . import fields
from .api import *


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs['_fields'] = {name: instance for name, instance in attrs.items()
                              if isinstance(instance, fields.BaseField)}
        super_new = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super_new
        return super_new


class BaseModel(object):
    __metaclass__ = ModelMeta

    _fields = {}

    def __init__(self, data=None, **kwargs):
        self.data = data
        if data is None and kwargs:
            self.data = kwargs
        for name, field in self._fields.items():
            new_field = copy(field)
            setattr(self, name, new_field)


class Company(BaseModel):

    type = fields.ConstantField('type', 'company')
    id = fields.Field('id')
    name = fields.Field('name')

    objects = CompanyManager()


class Lead(BaseModel):

    id = fields.Field('id')
    name = fields.Field('name')

    objects = LeadsManager()


class Contact(BaseModel):

    type = fields.ConstantField('type', 'contact')
    id = fields.Field('id')
    name = fields.Field('name')
    company = fields.ForeignField(Company, 'linked_company_id', ['company_name'])
    created_user = fields.Field('created_user_id')
    linked_leads = fields.ManyForeignField('linked_leads_id')

    date_create = fields.DateTimeField('date_create')
    last_modified = fields.DateTimeField('last_modified')

    tags = fields.ManyDictField('tags', 'name')
    deleted = fields.BooleanField('deleted')

    objects = ContactsManager()
