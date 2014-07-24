# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import time
from . import fields
from .api import *


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs['_fields'] = {name: instance for name, instance in attrs.items()
                              if isinstance(instance, fields.BaseField)}
        super_new = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        return super_new


class BaseModel(object):
    __metaclass__ = ModelMeta

    _fields = {}

    def __init__(self, data=None, **kwargs):
        self.data = data
        self.fields_data = {}
        if data is None and kwargs:
            self.data = kwargs

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def save(self, update_if_exists=True):
        if self.id is not None:
            return self.objects.update(**self.data)
        if update_if_exists:
            return self.objects.create_or_update(**self.data)
        return self.objects.create(**self.data)


class Company(BaseModel):

    type = fields.ConstantField('type', 'company')
    id = fields.UneditableField('id')
    name = fields.Field('name')
    address = fields.Field('address')

    objects = CompanyManager()


class Lead(BaseModel):

    id = fields.UneditableField('id')
    name = fields.Field('name')

    objects = LeadsManager()


class Contact(BaseModel):

    type = fields.ConstantField('type', 'contact')
    id = fields.UneditableField('id')
    name = fields.Field('name')
    email = fields.Field('email')
    company = fields.ForeignField(Company, 'linked_company_id', auto_created='company_name')
    company_name = fields.Field('company_name')
    created_user = fields.Field('created_user')
    linked_leads = fields.ManyForeignField('linked_leads_id')

    date_create = fields.DateTimeField('date_create')
    last_modified = fields.DateTimeField('last_modified')

    tags = fields.ManyDictField('tags', 'name')
    deleted = fields.BooleanField('deleted')

    objects = ContactsManager()

    def save(self, *args, **kwargs):
        if self.date_create is None:
            self.date_create = time.time()
        return BaseModel.save(self, *args, **kwargs)
