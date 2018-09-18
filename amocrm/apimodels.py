# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
import time
import copy
from datetime import datetime
import logging

import six
from pytz import utc, timezone

from . import fields
from .api import *


__all__ = ['BaseCompany', 'BaseContact', 'BaseLead',
           'CompanyTask', 'ContactTask', 'LeadTask',
           'CompanyNote', 'ContactNote', 'LeadNote', 'TaskNote']
KIEV = 'Europe/Kiev'
MOSCOW = 'Europe/Moscow'


logger = logging.getLogger(__name__)


class _ModelMeta(type):
    _model_registry = {}

    def __new__(mcs, name, bases, attrs):
        attrs.setdefault('_fields', {})
        for base in bases:
            for _name, _field in getattr(base, '_fields', {}).items():
                if _name not in attrs:
                    attrs[_name] = _field

        attrs['_fields'].update({name: instance for name, instance in attrs.items()
                                 if isinstance(instance, (fields._BaseField, fields.CustomField))})
        attrs['_required'] = [f.field for f in attrs['_fields'].values() if f.required]
        super_new = super(_ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        assert name not in mcs._model_registry, 'Model already registered: %s' % name
        mcs._model_registry[name] = super_new  # To resolve models by names later
        _manager = getattr(super_new, 'objects', None)
        if _manager:
            _manager._amo_model_class = super(_ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        return super_new

    @classmethod
    def _resolve_model_names(mcs):
        for model in mcs._model_registry.values():
            for attr_name, attr in model.__dict__.items():
                if attr_name.endswith('_model') and isinstance(attr, str):
                    setattr(model, attr_name, mcs._model_registry[attr])


class _BaseModel(six.with_metaclass(_ModelMeta)):

    _ELEMENT_TYPES = {
        'contact': 1,
        'lead': 2,
        'company': 3,
        'task': 4,
    }

    id = fields._UneditableField('id', required=True)
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
                if isinstance(field, fields.ManyForeignField):
                    continue
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
                    if isinstance(field, fields._UneditableField):
                        self._data[field.field] = value
                    else:
                        setattr(self, name, value)
                    self._changed_fields.append(field.field)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __getattribute__(self, name):
        get_attr = super(_BaseModel, self).__getattribute__
        value = get_attr(name)
        if (value is None and not get_attr('_loaded') and
                    name != 'id' and
                    get_attr('_data').get('id', None) is not None and
                    name in get_attr('_fields') and
                    get_attr('_fields')[name].field not in get_attr('_changed_fields')):
            get_attr('_init')()
            value = get_attr(name)
        return value

    get = __getitem__

    def _init(self):
        if not self._loaded and self.id is not None:
            amo_data = self.objects.get(self.id)  # trying to get info from crm
            if amo_data:
                self.__init__(amo_data._data, _loaded=True)
                return True

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
        if self.id and not self._data['id']:  # TODO: WTF ???
            self._data['id'] = self.id
        if self.date_create is None:
            self._data['date_create'] = int(time.time())
        current_last_modified = self._data.get('last_modified')
        now = int(time.time())
        if current_last_modified and current_last_modified > now:
            # Воркэраунд для ситуации, когда last_modified объекта на сервере больше, чем наше время
            logger.debug('last_modified workaround old last_modified=%s > now=%s', current_last_modified, now)
            self._data['last_modified'] = current_last_modified + 1
        else:
            self._data['last_modified'] = now
        for name, field in self._fields.items():
            if field.field in self._required:
                value = getattr(self, name)
                if not value:
                    continue
                if isinstance(field, fields._UneditableField):
                    self._data[field.field] = value
                else:
                    setattr(self, name, value)

        multi = [custom_field['name'] for custom_field in self.objects._custom_fields.values()
                 if custom_field['type_id'] == fields.MULTI_LIST_TYPE]
        if self._data.get(fields.CustomField._field, None):
            for field in multi:
                data = [cfield for cfield in self._data[fields.CustomField._field] if cfield.get('name', None) == field]
                data = data.pop() if data else None
                if data and data['values'] and isinstance(data['values'][0], dict):
                    data['values'] = [val['enum'] for val in data['values']]
            self._data[fields.CustomField._field] = [{key: value for key, value in cf.items() if key in ['id', 'values']}
                                                     for cf in self._data.get(fields.CustomField._field) if field in multi or cf['values'][0]['value']]

        if not self._loaded:
            for name, field in self._fields.items():
                if (isinstance(field, fields._BaseField) and field.required and getattr(self, name, None) is None)\
                        and not isinstance(field, fields._UneditableField):
                    raise ValueError('{} is required'.format(name))

    def save(self, update_if_exists=False):
        self._save_fk()
        self._pre_save()
        data = self._data
        if self.id is not None:
            method = self.objects.update
            if not self._changed_fields:
                return
            data = dict([(key, value) for key, value in data.items() if key in self._changed_fields or key in self._required])
        elif update_if_exists:
            method = self.objects.create_or_update
        else:
            method = self.objects.create
        result = method(**data)
        if result:
            self._data['id'] = result
        self._changed_fields = []
        self._fields_data = {}

    def _get_field_by_name(self, name):
        result = [v for k, v in self._fields.items() if v.field == name]
        return result.pop()

    def __str__(self):
        return '{self.__class__.__name__}({self.id})'.format(self=self)

    __repr__ = __str__

    def __hash__(self):
        return hash(self.id or json.dumps(self._data))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.id == other.id:
                return True
            return False
        elif isinstance(other, six.string_types):
            param = getattr(self, 'name', None) or getattr(self, 'text', None)
            if param:
                return param == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_copy(self):
        data = copy.deepcopy(self._data)
        data.pop('date_create')
        data.pop('id')
        return self.__class__(data=data, _loaded=True)

    @property
    def detail_url(self):
        if self.id:
            return self.objects._url('/{0}/detail/{1}'.format(self.objects.container_name, self.id))

    def delete(self):
        self.objects.delete(self.id)


class _AbstractNamedModel(_BaseModel):
    name = fields._Field('name', required=True)
    linked_leads = fields.ManyForeignField('linked_leads_id')
    tags = fields._TagsField('tags', 'name')


class BaseCompany(_AbstractNamedModel):
    contact_model = 'BaseContact'
    company_note_model = 'CompanyNote'
    company_task_model = 'CompanyTask'

    type = fields._ConstantField('type', 'company')

    objects = CompanyManager()

    @property
    def notes(self):
        return self.company_note_model.objects.all(query={'element_id': self.id})

    @property
    def tasks(self):
        return self.company_task_model.objects.all(query={'element_id': self.id})

    def create_note(self, text, note_type='COMMON'):
        note = self.company_note_model(company=self, type=note_type, text=text)
        note.save(update_if_exists=False)
        return note

    @property
    def contacts(self):
        return (
            self.contact_model.objects.get(_id)
            for _id in set([
                item['to_id']
                for item in self.objects._get_linkslist(
                    from_type='company',
                    from_ids=[self.id],
                    to_type='contact',
                )
                if item['to'] == 'contacts'
            ])
        )


class BaseLead(_BaseModel):
    contact_model = 'BaseContact'
    lead_task_model = 'LeadTask'
    lead_note_model = 'LeadNote'

    name = fields._Field('name', required=False)
    tags = fields._TagsField('tags', 'name')
    status = fields._StatusTypeField(required=True)
    pipeline = fields._TypeField('pipeline_id', choices='pipelines', required=False)
    company = fields.ForeignField(BaseCompany, 'linked_company_id',
                                  auto_created=True,
                                  links={'name': 'company_name'})
    budget = price = fields._Field('price')

    objects = LeadsManager()

    def create_task(self, text, complete_till, task_type='Follow-up'):
        task = self.lead_task_model(lead=self, type=task_type, text=text,
                                    complete_till=complete_till)
        task.save(update_if_exists=False)
        return task

    @property
    def tasks(self):
        return self.lead_task_model.objects.all(query={'element_id': self.id})

    def create_note(self, text, note_type='COMMON'):
        note = self.lead_note_model(lead=self, type=note_type, text=text)
        note.save(update_if_exists=False)
        return note

    @property
    def notes(self):
        return self.lead_note_model.objects.all(query={'element_id': self.id})

    @property
    def statuses(self):
        if self.pipeline and self.objects.pipelines[self.pipeline]:
            return {item.get('name', item.get('id')): item
                    for item in self.objects.pipelines[self.pipeline]['statuses'].values()}
        return self.objects.leads_statuses

    @property
    def contacts(self):
        return (self.contact_model.objects.get(_id) for _id in
                set([item['contact_id'] for item in self.objects._get_links(leads=[self.id])]))


class BaseContact(_AbstractNamedModel):
    lead_model = 'BaseLead'
    contact_note_model = 'ContactNote'
    contact_task_model = 'ContactTask'
    leads = fields.ManyForeignField(BaseLead, 'linked_leads_id')
    type = fields._ConstantField('type', 'contact')
    company = fields.ForeignField(BaseCompany, 'linked_company_id',
                                  auto_created=True,
                                  links={'name': 'company_name'})
    created_user = fields._UneditableField('created_user')

    objects = ContactsManager()

    def create_task(self, text, complete_till, task_type='Follow-up'):
        task = self.contact_task_model(contact=self, type=task_type, text=text,
                                       complete_till=complete_till)
        task.save(update_if_exists=False)
        return task

    @property
    def tasks(self):
        return self.contact_task_model.objects.all(query={'element_id': self.id})

    def create_note(self, text, note_type='COMMON'):
        note = self.contact_note_model(contact=self, type=note_type, text=text)
        note.save(update_if_exists=False)
        return note

    @property
    def notes(self):
        return self.contact_note_model.objects.all(query={'element_id': self.id})

    @property
    def links(self):
        return (self.lead_model.objects.get(item['lead_id'])
                for item in self.objects._get_links(contacts=[self.id]))


class _AbstractTaskModel(_BaseModel):
    CALL = 'Звонок'
    MEETING = 'Встреча'
    LETTER = 'Письмо'
    FOLLOW = 'Follow-up'

    type = fields._TypeField('task_type', 'task_types', required=True)
    text = fields._Field('text', required=True)
    complete_till = fields._DateTimeField('complete_till', required=True)
    is_closed = fields._BooleanField('status', required=True)

    objects = TasksManager()

    @property
    def is_active(self):
        if self.is_closed or self.complete_till < datetime.utcnow():
            return False
        return True

    def get_task_time_tz(self, tz=KIEV):
        return utc.localize(self.complete_till).astimezone(timezone(tz))

    @property
    def is_meeting(self):
        return self.type == 'Встреча'

    @property
    def is_full_day(self):
        return self.complete_till.minute == 59

    def delete(self):
        self.objects.delete(self.id, name='todo')


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
                                         _BaseModel._ELEMENT_TYPES['company'])

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
            res = {'TEXT': self.text}
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
                                          _BaseModel._ELEMENT_TYPES['company'])

    objects = NotesManager(object_type='company')


class TaskNote(_AbstractNoteModel):
    task_id = fields._Field('element_id')
    _element_type = fields._ConstantField('element_type',
                                          _BaseModel._ELEMENT_TYPES['task'])

    objects = NotesManager(object_type='task')


_ModelMeta._resolve_model_names()
