# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .base import _BlankMixin, _BaseAmoManager, _Helper


__all__ = ['AmoApi', 'NotesManager', 'ContactsManager', 'CompanyManager', 'LeadsManager', 'TasksManager']


class ContactsManager(_BlankMixin, _BaseAmoManager):
    name = 'contacts'
    _object_type = 'contact'

    def _add_data(self, **kwargs):
        kwargs.setdefault('responsible_user_id', self.rui)
        return super(ContactsManager, self)._add_data(**kwargs)


class CompanyManager(_BlankMixin, _BaseAmoManager):
    name = 'company'
    _object_type = name
    _main_field = 'name'


class LeadsManager(_BlankMixin, _BaseAmoManager):
    name = 'leads'


class _ObjectIdMixin(object):
    def __init__(self, object_type=None, *args, **kwargs):
        super(_ObjectIdMixin, self).__init__(*args, **kwargs)
        self._object_type = object_type


class TasksManager(_ObjectIdMixin, _BlankMixin, _BaseAmoManager):
    name = 'tasks'
    _main_field = 'element_id'

    def search(self, query):
            raise Exception('Amocrm havn\'t task search ability ')

    def _create_or_update_data(self, **data):
        return self.add(**data)


class NotesManager(_ObjectIdMixin, _BlankMixin, _BaseAmoManager):
    name = 'notes'
    _main_field = 'element_id'

    def search(self, query):
        raise Exception('Amocrm havn\'t note search ability ')

    def _create_or_update_data(self, **data):
        return self.add(**data)


class AmoApi(_Helper(ContactsManager, 'contacts'), _Helper(CompanyManager, 'company'),
             _Helper(NotesManager, 'notes'), _Helper(LeadsManager, 'leads'), _Helper(TasksManager, 'tasks'),
             _BlankMixin, _BaseAmoManager):
    name = 'accounts'

