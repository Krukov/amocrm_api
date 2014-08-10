# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import datetime

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

new_contact = Contact(name='Example2', company='ExampleCorp2', position='QA')
new_contact.site = 'http://example.com'
new_contact.save()

#===================

contact = Contact.objects.get(new_contact.id)
contact_search = Contact.objects.search('Example2')
assert contact.id == contact_search.id

contact.create_task('New task, yeee', task_type='Звонок',
                 complete_till=datetime.datetime.now()+datetime.timedelta(days=3))
print(contact.notes)
print(contact.tasks)
