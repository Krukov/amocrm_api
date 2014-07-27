# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .base import BlankMixin, BaseAmoManager, Helper


ELEMENT_TYPE = {
    'contact': 1,
    'deal': 2,
}


class NotesManager(BlankMixin, BaseAmoManager):
    name = 'notes'


class ContactsManager(BlankMixin, BaseAmoManager):
    name = 'contacts'


class CompanyManager(BlankMixin, BaseAmoManager):
    name = 'company'
    object_type = name
    _main_field = 'name'


class LeadsManager(BlankMixin, BaseAmoManager):
    name = 'leads'


class TasksManager(BlankMixin, BaseAmoManager):
    name = 'tasks'


class AmoApi(Helper(ContactsManager, 'contacts'), Helper(CompanyManager, 'company'),
             Helper(NotesManager, 'notes'), Helper(LeadsManager, 'leads'), Helper(TasksManager, 'tasks'),
             BlankMixin, BaseAmoManager):
    name = 'accounts'

