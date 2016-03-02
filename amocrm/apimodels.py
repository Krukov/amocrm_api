# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import time
import six

from . import fields
from .api import *
from .utils import lazy_property


__all__ = ['BaseCompany', 'BaseContact', 'ContactTask', 'LeadTask', 'BaseLead', 'ContactNote', 'LeadNote']


class _ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('_fields', {})
        [attrs.update(getattr(base, '_fields', {})) for base in bases]
        attrs['_fields'].update({name: instance for name, instance in attrs.items()
                                 if isinstance(instance, fields._BaseField) or isinstance(instance, fields.CustomField)})
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

    id = fields._UneditableField('id')
    date_create = fields._StaticDateTimeField('date_create')
    last_modified = fields._StaticDateTimeField('last_modified')
    request = fields._Field('request_id')
    amo_user = rui = fields.Owner()
    amo_creator = fields.Owner('created_user_id')

    def __init__(self, data=None, **kwargs):
        self._data, self._init_data = {}, {}
        self._fields_data, self._changed_fields = {}, []
        self._loaded = bool(kwargs.pop('_loaded', False))
        if self._loaded:
            self._data = data or kwargs
        else:
            self._init_data = data or kwargs

            for name, field in self._fields.items():
                value = self._init_data.get(name, None) or getattr(self, name)
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
                    if isinstance(field, fields._UneditableField):
                        self._data[field.field] = value
                    else:
                        setattr(self, name, value)
                    self._changed_fields.append(field.field)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __getattribute__(self, name):
        value = super(_BaseModel, self).__getattribute__(name)
        if (value is None and not self._loaded and name != 'id' and self.id is not None and name in self._fields
                and self._fields[name].field not in self._changed_fields):
            amo_data = self.objects.get(self.id)  # trying to get info from crm
            if amo_data:
                self.__init__(amo_data._data, _loaded=True)
        return value or super(_BaseModel, self).__getattribute__(name)

    get = __getitem__

    def _save_fk(self):
        for name, field in self._fields.items():
            if not isinstance(field, fields.ForeignField):
                continue
            main_field = field.object_type.objects._main_field
            if main_field is not None and main_field in field.links:
                value = getattr(getattr(self, name), main_field)
                self._data[field.links[main_field]] = value
            if getattr(field, 'auto', None):
                continue
            if (field.field in self._changed_fields or not self._loaded) \
                    and (name in self._data or name in self._init_data):
                if not getattr(self, name).id:  # save fk if it not exists
                    getattr(self, name).save()
                self._data[field.field] = getattr(self, name).id

    def _pre_save(self):
        if self.date_create is None:
            self._data['date_create'] = int(time.time())
        self._data['last_modified'] = int(time.time())
        multi = [custom_field['name'] for custom_field in self.objects._custom_fields.values()
                 if custom_field['type_id'] == fields.MULTI_LIST_TYPE]
        if self._data.get(fields.CustomField._field, None):
            for field in multi:
                data = [cfield for cfield in self._data[fields.CustomField._field] if cfield.get('name', None) == field]
                data = data.pop() if data else None
                if data and data['values'] and isinstance(data['values'][0], dict):
                    data['values'] = [val['enum'] for val in data['values']]

        if not self._loaded:
            for name, field in self._fields.items():
                if (isinstance(field, fields._BaseField) and
                        field.required and getattr(self, name, None) is None):
                    raise ValueError('{} is required'.format(name))

    def save(self, update_if_exists=True):
        self._save_fk()
        self._pre_save()
        data = self._data
        if self.id is not None:
            method = self.objects.update
            if not self._changed_fields:
                return
            data = dict([(key, value) for key, value in data.items() if key in self._changed_fields or key == 'id'])
        elif update_if_exists:
            method = self.objects.create_or_update
        else:
            method = self.objects.create
        result = method(**data)
        self._data['id'] = result

    def _get_field_by_name(self, name):
        result = [v for k, v in self._fields.items() if v.field == name]
        return result.pop()

    def __str__(self):
        return '{self.__class__.__name__}({self.id})'.format(self=self)

    __repr__ = __str__

    def __hash__(self):
        return hash(self.id or json.dumps(self._data))

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def detail_url(self):
        if self.id:
            return self.objects._url('/{0}/detail/{1}'.format(self.objects.name, self.id))


class _AbstractNamedModel(_BaseModel):
    name = fields._Field('name', required=True)
    linked_leads = fields.ManyForeignField('linked_leads_id')
    tags = fields._TagsField('tags', 'name')


class BaseCompany(_AbstractNamedModel):
    type = fields._ConstantField('type', 'company')

    objects = CompanyManager()

    @lazy_property
    def notes(self):
        return CompanyNote.objects.all(query={'element_id': self.id})

    @lazy_property
    def tasks(self):
        return CompanyTask.objects.all(query={'element_id': self.id})


class BaseLead(_AbstractNamedModel):
    contact_model = None
    status = fields._StatusTypeField(required=True)
    pipeline = fields._TypeField('pipeline_id', choices='pipelines', required=False)
    budget = price = fields._Field('price')

    objects = LeadsManager()

    def create_task(self, text, task_type=None, complete_till=None):
        task = LeadTask(lead=self, type=task_type, text=text, complete_till=complete_till)
        task.save()
        return task

    @property
    def tasks(self):
        return LeadTask.objects.all(query={'element_id': self.id})

    def create_note(self, text, note_type='COMMON'):
        note = LeadNote(lead=self, type=note_type, text=text)
        note.save()
        return note

    @property
    def notes(self):
        return LeadNote.objects.all(query={'element_id': self.id})

    @property
    def statuses(self):
        if self.pipeline and self.objects.pipelines[self.pipeline]:
            return {item.get('name', item.get('id')): item for item in self.objects.pipelines[self.pipeline]['statuses'].values()}
        return self.objects.leads_statuses

    @property
    def contacts(self):
        return (self.contact_model.objects.get(_id) for _id in
                set([item['contact_id'] for item in self.objects._get_links(leads=[self.id])]))


class BaseContact(_AbstractNamedModel):
    leads_model = None
    leads = fields.ManyForeignField(BaseLead, 'linked_leads_id')
    type = fields._ConstantField('type', 'contact')
    company = fields.ForeignField(BaseCompany, 'linked_company_id',
                                  auto_created=True,
                                  links={'name': 'company_name'})
    created_user = fields._UneditableField('created_user')

    objects = ContactsManager()

    def create_task(self, text, task_type=None, complete_till=None):
        task = ContactTask(contact=self, type=task_type, text=text, complete_till=complete_till)
        task.save()
        return task

    @lazy_property
    def tasks(self):
        return ContactTask.objects.all(query={'element_id': self.id})

    def create_note(self, text, note_type='COMMON'):
        note = ContactNote(contact=self, type=note_type, text=text)
        note.save()
        return note

    @lazy_property
    def notes(self):
        return ContactNote.objects.all(query={'element_id': self.id})

    @property
    def links(self):
        return (self.leads_model.objects.get(item['lead_id']) for item in self.objects._get_links(contacts=[self.id]))


class _AbstractTaskModel(_BaseModel):
    type = fields._TypeField('task_type', 'task_types', required=True)
    text = fields._Field('text', required=True)
    complete_till = fields._DateTimeField('complete_till', required=True)
    is_closed = fields._BooleanField('status', required=True)

    objects = TasksManager()


class LeadTask(_AbstractTaskModel):
    lead = fields.ForeignField(BaseLead, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                         _BaseModel._ELEMENT_TYPES['lead'])

    objects = TasksManager(object_type='lead')


class ContactTask(_AbstractTaskModel):
    contact = fields.ForeignField(BaseContact, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                         _BaseModel._ELEMENT_TYPES['contact'])

    objects = TasksManager(object_type='contact')


class CompanyTask(_AbstractTaskModel):
    company = fields.ForeignField(BaseCompany, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                         _BaseModel._ELEMENT_TYPES['contact'])

    objects = TasksManager(object_type='company')


class _AbstractNoteModel(_BaseModel):
    type = fields._TypeField('note_type', 'note_types', required=True)
    text = fields._Field('text', required=True)

    objects = NotesManager()

    @property
    def properties(self):
        try:
            res = json.loads(self.text)
        except ValueError:
            res = None
        if not isinstance(res, dict):
            res = {u'TEXT': self.text}
        return res


class LeadNote(_AbstractNoteModel):
    lead = fields.ForeignField(BaseLead, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                          _BaseModel._ELEMENT_TYPES['lead'])

    objects = NotesManager(object_type='lead')


class ContactNote(_AbstractNoteModel):
    contact = fields.ForeignField(BaseContact, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                          _BaseModel._ELEMENT_TYPES['contact'])

    objects = NotesManager(object_type='contact')


class CompanyNote(_AbstractNoteModel):
    company = fields.ForeignField(BaseCompany, 'element_id')
    _element_type = fields._ConstantField('element_type',
                                          _BaseModel._ELEMENT_TYPES['contact'])

    objects = NotesManager(object_type='company')
