==================
AmoCRM python API. 
==================

Вопросы?

.. image:: https://badges.gitter.im/Krukov/amocrm_api.svg
   :alt: Join the chat at https://gitter.im/Krukov/amocrm_api
   :target: https://gitter.im/Krukov/amocrm_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

------------------
Могу оказать помощь по экспорту/импроту ваших данных из/в AmoCRM
------------------

.. image:: https://travis-ci.org/Krukov/amocrm_api.svg?branch=master
    :target: https://travis-ci.org/Krukov/amocrm_api
.. image:: https://img.shields.io/coveralls/Krukov/amocrm_api.svg
    :target: https://coveralls.io/r/Krukov/amocrm_api


Python AmoCRM API (http://www.amocrm.ru/) (human interface for easy using )


Installation
============

::

    pip install amocrm_api


Usage
=====


There are 7 abstraction of 5 AmoCRM objects:

- Контакт - BaseContact
- Компания  - BaseCompany
- Сделка - BaseLead
- Задача - (LeadTask, ContactTask)
- Событие - (LeadNote, ContactNote)

Settings
--------

First of all you need to define settings
Example::

    from amocrm import BaseContact, amo_settings, fields
    amo_settings.set('krukov@centrobit.ru', '4b332718c4c5944003af7e6389860ced', 'testcentrobit')


Custom field
------------

One of the features of AmoCRM in the presence of custom fields in a contact, company and lead objects

To define your custom field you need describe it

Example::

    from amocrm import BaseContact, amo_settings, fields
    amo_settings.set('krukov@centrobit.ru', '4b332718c4c5944003af7e6389860ced', 'testcentrobit')

    class Contact(BaseContact):
        position = fields.CustomField(u'Должность')
        site = fields.CustomField(u'Сайт')
        phone = fields.EnumCustomField(u'Телефон', enum='WORK')

Ok, now it is ready to use and you can get, create or edit contacts

Example::

    new_contact = Contact(name='Example2', company='ExampleCorp2', position='QA', phone='0001')
    new_contact.site = 'http://example.com'
    new_contact.save()

    contact = Contact.objects.get(new_contact.id)
    contact_search = Contact.objects.search('Example2')
    assert contact.id == contact_search.id
    print(contact.phone)
    contact.phone = '8-800-00000000'
    contact.save()
    contact.create_task('New task, yeee', task_type=u'Звонок',
                     complete_till=datetime.datetime.now()+datetime.timedelta(days=3))
    print(contact.notes)
    print(contact.tasks)

