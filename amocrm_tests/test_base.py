# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import copy
import unittest
from datetime import datetime, timedelta

from amocrm import amo_settings, BaseContact, BaseCompany, BaseLead, ContactTask,\
    ContactNote, LeadTask, LeadNote, fields
from amocrm.test_utils import amomock

from_ts = datetime.fromtimestamp


class AmoSettingsMixin(object):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        amo_settings.set('test', 'test', 'test')


class CreateObjMixin(object):
    object_type = None
    create_param = {}

    def create_object(self, object=None, **kwargs):
        data = copy.deepcopy(self.create_param)
        data.update(kwargs)
        _type = object or self.object_type
        _object = _type(data)
        _object.save()
        return _object

    @property
    def object(self):
        return self.create_object()


class TestCreations(AmoSettingsMixin, unittest.TestCase):

    @amomock.activate
    def test_creating_contact(self):
        contact = BaseContact(name='test', tags=['1', '2', 'frog'], created_user=1)
        self.assertIsNone(contact.id)
        self.assertEqual(contact.type, 'contact')
        self.assertEqual(contact.name, 'test')
        self.assertEqual(contact.tags, ['1', '2', 'frog'])
        self.assertEqual(contact.created_user, 1)
        self.assertIsNone(contact.date_create)
        self.assertIsNone(contact.last_modified)
        self.assertIsNone(contact.amo_user)

        contact.save()
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)
        self.assertEqual(contact.created_user, 1)

        _contact = BaseContact.objects.get(contact.id)
        self.assertEqual(_contact.id, contact.id)
        self.assertEqual(_contact.type, 'contact')
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.tags, ['1', '2', 'frog'])
        self.assertEqual(_contact.created_user, 1)
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)

    @amomock.activate
    def test_creating_company(self):
        company = BaseCompany(name='test', tags=['1', '2', 'frog'])
        self.assertIsNone(company.id)
        self.assertEqual(company.type, 'company')
        self.assertEqual(company.name, 'test')
        self.assertEqual(company.tags, ['1', '2', 'frog'])
        self.assertIsNone(company.last_modified)
        self.assertIsNone(company.date_create)

        company.save()
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)

        _company = BaseCompany.objects.get(company.id)
        self.assertEqual(_company.id, company.id)
        self.assertEqual(_company.type, 'company')
        self.assertEqual(_company.name, 'test')
        self.assertEqual(_company.tags, ['1', '2', 'frog'])
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)

    @amomock.activate
    def test_lead_create(self):

        lead = BaseLead(name='test', status='test2', price=10000.00)
        self.assertEqual(lead.name, 'test')
        self.assertEqual(lead.status, 'test2')
        self.assertEqual(lead.price, 10000)
        self.assertIsNone(lead.id)

        lead.save()
        self.assertEqual(lead.name, 'test')
        self.assertEqual(lead.status, 'test2')
        self.assertEqual(lead.price, 10000)
        self.assertEqual(lead.id, 1)
        
        _lead = BaseLead.objects.get(lead.id)
        self.assertEqual(_lead.name, 'test')
        self.assertEqual(_lead.status, 'test2')
        self.assertEqual(_lead.price, 10000)
        self.assertEqual(_lead.id, 1)

    @amomock.activate
    def test_contact_task_create(self):
        contact = BaseContact(name='test')
        contact.save()

        complete_date = datetime.now()+timedelta(days=3)
        task = ContactTask(contact=contact, text='test task text', type='Call',
                           complete_till=complete_date)
        self.assertEqual(task.contact.name, 'test')
        self.assertEqual(task.contact.id, contact.id)
        self.assertEqual(task.text, 'test task text')
        self.assertEqual(task.complete_till.date(), complete_date.date())

        task.save()
        self.assertEqual(task.contact.name, 'test')
        self.assertEqual(task.contact.id, contact.id)
        self.assertEqual(task.text, 'test task text')
        self.assertEqual(task.complete_till.date(), complete_date.date())

        _task = ContactTask.objects.get(task.id)
        self.assertEqual(_task.contact.name, 'test')
        self.assertEqual(_task.contact.id, contact.id)
        self.assertEqual(_task.text, 'test task text')
        self.assertEqual(_task._element_type, ContactTask._ELEMENT_TYPES['contact'])
        self.assertEqual(_task.complete_till.date(), complete_date.date())

    @amomock.activate
    def test_lead_task_create(self):
        lead = BaseLead(name='test', status='test1')
        lead.save()

        complete_date = datetime.now()+timedelta(days=3)
        task = LeadTask(lead=lead, text='test task text', type='Call', complete_till=complete_date)
        self.assertEqual(task.lead.name, 'test')
        self.assertEqual(task.lead.id, lead.id)
        self.assertEqual(task.text, 'test task text')
        self.assertEqual(task.complete_till.date(), complete_date.date())

        task.save()
        self.assertEqual(task.lead.name, 'test')
        self.assertEqual(task.lead.id, lead.id)
        self.assertEqual(task.text, 'test task text')
        self.assertEqual(task.complete_till.date(), complete_date.date())

        _task = LeadTask.objects.get(task.id)
        self.assertEqual(_task.lead.name, 'test')
        self.assertEqual(_task.lead.id, lead.id)
        self.assertEqual(_task.text, 'test task text')
        self.assertEqual(_task._element_type, LeadTask._ELEMENT_TYPES['lead'])
        self.assertEqual(_task.complete_till.date(), complete_date.date())

    @amomock.activate
    def test_contact_note_create(self):
        contact = BaseContact(name='test')
        contact.save()

        note = ContactNote(contact=contact, text='test note text', type='COMMON')
        self.assertEqual(note.contact.name, 'test')
        self.assertEqual(note.contact.id, contact.id)
        self.assertEqual(note.text, 'test note text')

        note.save()
        self.assertEqual(note.contact.name, 'test')
        self.assertEqual(note.contact.id, contact.id)
        self.assertEqual(note.text, 'test note text')

        _note = ContactNote.objects.get(note.id)
        self.assertEqual(_note.contact.name, 'test')
        self.assertEqual(_note.contact.id, contact.id)
        self.assertEqual(_note.text, 'test note text')
        self.assertEqual(_note._element_type, ContactTask._ELEMENT_TYPES['contact'])

    @amomock.activate
    def test_lead_note_create(self):
        lead = BaseLead(name='test', status='test1')
        lead.save()

        note = LeadNote(lead=lead, text='test note text', type='DEAL_CREATED')
        self.assertEqual(note.lead.name, 'test')
        self.assertEqual(note.lead.id, lead.id)
        self.assertEqual(note.text, 'test note text')

        note.save()
        self.assertEqual(note.lead.name, 'test')
        self.assertEqual(note.lead.id, lead.id)
        self.assertEqual(note.text, 'test note text')

        _note = LeadNote.objects.get(note.id)
        self.assertEqual(_note.lead.name, 'test')
        self.assertEqual(_note.lead.id, lead.id)
        self.assertEqual(_note.text, 'test note text')
        self.assertEqual(_note._element_type, LeadTask._ELEMENT_TYPES['lead'])


class TestContacts(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    create_param = dict(name='test_name', tags=['1', '2', '3'], created_user=731)
    object_type = BaseContact

    @amomock.activate
    def test_getting_contact_by_id_and_data(self):
        created = self.create_object()
        contact = BaseContact.objects.get(created.id)

        self.assertEqual(contact.name, 'test_name')
        self.assertEqual(contact.id, created.id)
        self.assertSetEqual(set(contact.tags), set(['1', '2', '3']))
        self.assertEquals(contact.created_user, 731)

    @amomock.activate
    def test_searching_contact(self):
        self.create_object()
        self.create_object(name='super_uniq')
        contact = BaseContact.objects.search('super_uniq').pop()
        self.assertEqual(contact.name, 'super_uniq')

    @amomock.activate
    def test_edit_contact(self):
        created = self.create_object()
        contact = BaseContact.objects.get(created.id)
        self.assertNotEqual(contact.name, 'frog')
        contact.name = 'frog'
        contact.save()

        _contact = BaseContact.objects.get(created.id)
        self.assertEqual(_contact.name, 'frog')

    @amomock.activate
    def test_creating_tags(self):
        created = self.create_object(tags=['Tag2', 'Tag1'])

        _contact = BaseContact.objects.get(created.id)
        self.assertEqual(_contact.tags, ['Tag2', 'Tag1'])

        _contact.tags += ['frog']
        _contact.save()
        _contact = BaseContact.objects.get(created.id)
        self.assertEqual(_contact.tags, ['Tag2', 'Tag1', 'frog'])

    @amomock.activate
    def test_required_fields(self):
        contact = self.object_type()
        with self.assertRaises(ValueError) as context:
            contact.save()
        self.assertEqual('name is required', str(context.exception))


class TestCompany(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = BaseCompany
    create_param = {'name': 'test_name'}

    @amomock.activate
    def test_getting_company_by_id_and_data(self):
        created = self.create_object()
        company = self.object_type.objects.get(created.id)

        self.assertEqual(company.id, created.id)
        self.assertEqual(company.name, 'test_name')

    @amomock.activate
    def test_searching_company(self):
        self.create_object()
        self.create_object(name='super_uniq')
        company = self.object_type.objects.search('super_uniq').pop()
        self.assertEqual(company.name, 'super_uniq')

    @amomock.activate
    def test_edit_company(self):
        created = self.create_object()
        company = self.object_type.objects.get(created.id)
        self.assertNotEqual(company.name, 'frog')
        company.name = 'frog'
        company.save()

        _company = self.object_type.objects.get(created.id)
        self.assertEqual(_company.name, 'frog')

    @amomock.activate
    def test_required_fields(self):
        company = self.object_type()
        with self.assertRaises(ValueError) as context:
            company.save()
        self.assertEqual('name is required', str(context.exception))


class TestTask(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = ContactTask
    create_param = {'name': 'test_name', 'type': 'Call',
                    'complete_till': datetime.now()+timedelta(days=3), 'text': 'text test'}

    @amomock.activate
    def test_getting_task_by_id_and_data(self):
        contact = self.create_object(object=BaseContact)
        created = self.create_object(contact=contact, text='TEST TEST')
        task = self.object_type.objects.get(created.id)

        self.assertEqual(task.id, created.id)
        self.assertEqual(task.text, 'TEST TEST')
        self.assertEquals(task.contact.name, 'test_name')
        self.assertEquals(task.contact.id, contact.id)

    @amomock.activate
    def test_searching_task(self):
        self.assertRaises(Exception, self.object_type.objects.search)

    @amomock.activate
    def test_edit_task(self):
        created = self.create_object()
        task = self.object_type.objects.get(created.id)
        self.assertNotEqual(task.text, 'frog')
        task.text = 'frog'
        task.save()

        _task = self.object_type.objects.get(task.id)
        self.assertEqual(_task.text, 'frog')

    @amomock.activate
    def test_required_fields(self):
        task = self.object_type(text='x', complete_till=datetime.now())

        with self.assertRaises(ValueError) as context:
            task.save()
        self.assertEqual('type is required', str(context.exception))

        task.complete_till = None
        task.type = 'Call'
        with self.assertRaises(ValueError) as context:
            task.save()
        self.assertEqual('complete_till is required', str(context.exception))

        task.text = None
        task.complete_till = datetime.now()
        with self.assertRaises(ValueError) as context:
            task.save()
        self.assertEqual('text is required', str(context.exception))


class TestLead(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = BaseLead
    create_param = {'name': 'test_name', 'price': 100, 'status': 'test1'}

    @amomock.activate
    def test_getting_lead_by_id_and_data(self):
        created = self.create_object()
        lead = self.object_type.objects.get(created.id)

        self.assertEqual(lead.name, 'test_name')
        self.assertEqual(lead.id, created.id)

    @amomock.activate
    def test_searching_lead(self):
        self.create_object()
        self.create_object(name='super_uniq', price=999)
        lead = self.object_type.objects.search('super_uniq').pop()
        self.assertEqual(lead.name, 'super_uniq')

    @amomock.activate
    def test_edit_lead(self):
        self.create_object()
        lead = self.object_type.objects.get(1)
        self.assertNotEqual(lead.name, 'frog')
        lead.name = 'frog'
        lead.save()

        _lead = self.object_type.objects.get(1)
        self.assertEqual(_lead.name, 'frog')

    @amomock.activate
    def test_required_fields(self):
        lead = self.object_type(name='test1')

        with self.assertRaises(ValueError) as context:
            lead.save()
        self.assertEqual('status is required', str(context.exception))

    @amomock.activate
    def test_last_modified_since(self):
        self.create_object()
        leads = list(self.object_type.objects.all(modified_since=datetime.today()-timedelta(days=2)))
        call = amomock.calls[-1]
        self.assertIn('if-modified-since', call[0].headers)


class TestNote(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = ContactNote
    create_param = {'name': 'test_name', 'text': 'text test', 'type': 'COMMON'}

    @amomock.activate
    def test_getting_note_by_id_and_data(self):
        contact = self.create_object(object=BaseContact)
        created = self.create_object(contact=contact, text='TEST TEST')
        note = self.object_type.objects.get(created.id)

        self.assertEqual(note.id, created.id)
        self.assertEqual(note.text, 'TEST TEST')
        self.assertEquals(note.contact.name, 'test_name')
        self.assertEquals(note.contact.id, contact.id)

    @amomock.activate
    def test_searching_note(self):
        self.assertRaises(Exception, self.object_type.objects.search)

    @amomock.activate
    def test_edit_note(self):
        self.create_object()
        note = self.object_type.objects.get(1)
        self.assertNotEqual(note.text, 'frog')
        note.text = 'frog'
        note.save()

        _note = self.object_type.objects.get(1)
        self.assertEqual(_note.text, 'frog')


class TestCustomFields(AmoSettingsMixin, unittest.TestCase):
    @amomock.activate
    def test_contact_cf(self):

        class Contact(BaseContact):
            phone = fields.CustomField('Телефон')
            email = fields.CustomField('Email')

        contact = Contact(phone='8-888-888-88-88', email='test@email.com')
        contact.name = 'test'
        self.assertEqual(contact.phone, '8-888-888-88-88')
        self.assertEqual(contact.email, 'test@email.com')
        self.assertEqual(contact.name, 'test')

        contact.save()
        self.assertEqual(contact.phone, '8-888-888-88-88')
        self.assertEqual(contact.email, 'test@email.com')
        self.assertEqual(contact.name, 'test')

        contact = Contact.objects.get(contact.id)
        self.assertEqual(contact.phone, '8-888-888-88-88')

        self.assertEqual(contact.email, 'test@email.com')
        self.assertEqual(contact.name, 'test')


if __name__ == '__main__':
    unittest.main()
