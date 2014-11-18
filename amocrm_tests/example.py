# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import datetime

import logging

logging.getLogger('amocrm').setLevel(logging.DEBUG)


# LOW level API
from amocrm import AmoApi

amo_api = AmoApi('krukov@centrobit.ru', '4b332718c4c5944003af7e6389860ced', 'testcentrobit')

new_contact = amo_api.contacts.create_or_update(name='Example', company_name='ExampleComp', on_field='name')

note_types = amo_api.note_types
amo_api.notes.add(element_id=new_contact, element_type=1, note_type=note_types['COMMON']['id'], text='Example text')

print(new_contact)
print(amo_api.contacts.all())


## HIGH level API
from amocrm import BaseContact, amo_settings, fields

amo_settings.set('krukov@centrobit.ru', '4b332718c4c5944003af7e6389860ced', 'testcentrobit')


class Contact(BaseContact):
    position = fields.CustomField('Должность')
    site = fields.CustomField('Сайт')
    phone = fields.CustomField('Телефон', enum='WORK')

new_contact = Contact(name='Example2', company='ExampleCorp2', position='QA', phone='0001')
new_contact.site = 'http://example.com'
new_contact.save()

#===================

contact = Contact.objects.get(new_contact.id)
contact_search = Contact.objects.search('Example2')
assert contact.id == contact_search.id
print(contact.phone)
contact.phone = '8-800-00000000'
contact.save()
contact.create_task('New task, yeee', task_type='Звонок',
                 complete_till=datetime.datetime.now()+datetime.timedelta(days=3))
print(contact.notes)
print(contact.tasks)

#===================

from amocrm import BaseLead, LeadTask, amo_settings

amo_settings.set('krukov@centrobit.ru', '4b332718c4c5944003af7e6389860ced', 'testcentrobit')

lead = BaseLead(name=u'some name')
lead.save()
task = LeadTask(lead=lead, text='123', type=u'Звонок',
                complete_till=datetime.datetime.now()+datetime.timedelta(days=3))
task.save()
print(task.id)

leads = LeadTask.objects.all(modified_since=datetime.datetime.now()-datetime.timedelta(days=1))