# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from . import fields
from .api import *


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super_new
            super_new.__fields = {name: instance for name, instance in attrs.items()
                                  if isinstance(instance, fields.BaseField)}
        return super_new


class BaseModel(object):
    __metaclass__ = ModelMeta

    __fields = {}

    def __init__(self, data=None):
        self.data = data


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
