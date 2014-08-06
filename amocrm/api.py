# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .base import BlankMixin, BaseAmoManager, Helper


__all__ = ['AmoApi', 'NotesManager', 'ContactsManager', 'CompanyManager', 'LeadsManager', 'TasksManager']


class NotesManager(BlankMixin, BaseAmoManager):
    name = 'notes'


class ContactsManager(BlankMixin, BaseAmoManager):
    name = 'contacts'

    def add_data(self, **kwargs):
        kwargs.setdefault('responsible_user_id', self.rui)
        return super(ContactsManager, self).add_data(**kwargs)


class CompanyManager(BlankMixin, BaseAmoManager):
    name = 'company'
    _object_type = name
    _main_field = 'name'


class LeadsManager(BlankMixin, BaseAmoManager):
    name = 'leads'


class TasksManager(BlankMixin, BaseAmoManager):
    name = 'tasks'


class AmoApi(Helper(ContactsManager, 'contacts'), Helper(CompanyManager, 'company'),
             Helper(NotesManager, 'notes'), Helper(LeadsManager, 'leads'), Helper(TasksManager, 'tasks'),
             BlankMixin, BaseAmoManager):
    name = 'accounts'

