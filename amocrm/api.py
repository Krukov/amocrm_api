# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .base import _BlankMixin, _BaseAmoManager, _Helper
from .utils import lazy_dict_property

import six

__all__ = ['AmoApi', 'NotesManager', 'ContactsManager', 'CompanyManager', 'LeadsManager', 'TasksManager']


class ContactsManager(_BlankMixin, _BaseAmoManager):
    name = 'contacts'
    _main_field = 'name'
    _object_type = 'contact'

    def _add_data(self, **kwargs):
        kwargs.setdefault('responsible_user_id', self.user.id)
        return super(ContactsManager, self)._add_data(**kwargs)


class CompanyManager(_BlankMixin, _BaseAmoManager):
    name = 'company'
    _container_name = 'contacts'
    _object_type = name
    _main_field = 'name'

    @lazy_dict_property
    def _custom_fields(self):
        return self.get_custom_fields(to='companies')


class LeadsManager(_BlankMixin, _BaseAmoManager):
    name = 'leads'
    PRIMARY = u'Первичный контакт'
    CONVERSATION = u'Переговоры'
    DECIDE = u'Принимают решение'
    APPROVAL = u'Согласование договора'
    NOT_REALIZED = u'Закрыто и не реализовано'
    SUCCESSFULLY = u'Успешно реализовано'

    def all(self, query=None, status=None, **kwargs):
        query = query or {}
        if status:
            status = [status] if not isinstance(status, (list, tuple)) else status
            new_statuses = []
            for _status in status:
                if not ((isinstance(_status, six.string_types) and _status.isdigit()) or isinstance(_status, int)):
                    new_statuses.extend([k for k, v in self.all_leads_statuses.items() if v['name'] == _status])
                else:
                    new_statuses.append(_status)
            query['status'] = new_statuses
        return super(LeadsManager, self).all(query=query, **kwargs) or ()


class _ObjectIdMixin(object):
    def __init__(self, object_type=None, *args, **kwargs):
        super(_ObjectIdMixin, self).__init__(*args, **kwargs)
        self._object_type = object_type


class TasksManager(_ObjectIdMixin, _BlankMixin, _BaseAmoManager):
    name = 'tasks'
    _main_field = 'element_id'

    def search(self, *args, **kwargs):
        raise Exception('Amocrm havn\'t task search ability ')

    def _create_or_update_data(self, **data):
        return self.add(**data)


class NotesManager(_ObjectIdMixin, _BlankMixin, _BaseAmoManager):
    name = 'notes'
    _main_field = 'element_id'
    EXTERNAL_ATTACH = u'EXTERNAL_ATTACH'
    MAX_SYSTEM = u'MAX_SYSTEM'
    DEAL_STATUS_CHANGED = u'DEAL_STATUS_CHANGED'
    ATTACHEMENT = u'ATTACHEMENT'
    MAIL_MESSAGE = u'MAIL_MESSAGE'
    COMPANY_CREATED = u'COMPANY_CREATED'
    SMS_IN = u'SMS_IN'
    CALL_OUT = u'CALL_OUT'
    CONTACT_CREATED = u'CONTACT_CREATED'
    DEAL_CREATED = u'DEAL_CREATED'
    CALL = u'CALL'
    COMMON = u'COMMON'
    TASK_RESULT = u'TASK_RESULT'
    SMS_OUT = u'SMS_OUT'
    MAIL_MESSAGE_ATTACHMENT = u'MAIL_MESSAGE_ATTACHMENT'
    DROPBOX = u'DROPBOX'
    CALL_IN = u'CALL_IN'

    def search(self, *args, **kwargs):
        raise Exception('Amocrm havn\'t note search ability ')

    def _create_or_update_data(self, **data):
        return self.add(**data)


class AmoApi(_Helper(ContactsManager, 'contacts'), _Helper(CompanyManager, 'company'),
             _Helper(NotesManager, 'notes'), _Helper(LeadsManager, 'leads'), _Helper(TasksManager, 'tasks'),
             _BlankMixin, _BaseAmoManager):
    name = 'accounts'

