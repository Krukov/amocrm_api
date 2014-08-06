# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import copy
import unittest
import time
from datetime import datetime

from amocrm import *
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
        contact = Contact(name='test', tags=['1', '2', 'frog'], created_user=1)
        self.assertIsNone(contact.id)
        self.assertEqual(contact.type, 'contact')
        self.assertEqual(contact.name, 'test')
        self.assertEqual(contact.tags, ['1', '2', 'frog'])
        self.assertEqual(contact.created_user, 1)
        self.assertIsNone(contact.date_create)
        self.assertIsNone(contact.last_modified)
        self.assertIsNone(contact.rui)
        self.assertFalse(contact.deleted)

        contact.save()
        self.assertEqual(contact.id, 1)
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)
        self.assertEqual(contact.created_user, 1)
        self.assertFalse(contact.deleted)

        _contact = Contact.objects.get(contact.id)
        self.assertEqual(_contact.id, 1)
        self.assertEqual(_contact.type, 'contact')
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.tags, ['1', '2', 'frog'])
        self.assertEqual(_contact.created_user, 1)
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)
        self.assertEqual(_contact.date_create.date(), datetime.now().date())
        self.assertEqual(int(_contact.rui), int(99))
        self.assertFalse(_contact.deleted)

    @amomock.activate
    def test_creating_company(self):
        company = Company(name='test', tags=['1', '2', 'frog'])
        self.assertIsNone(company.id)
        self.assertEqual(company.type, 'company')
        self.assertEqual(company.name, 'test')
        self.assertEqual(company.tags, ['1', '2', 'frog'])
        self.assertIsNone(company.last_modified)
        self.assertIsNone(company.date_create)
        self.assertFalse(company.deleted)

        company.save()
        self.assertEqual(company.id, 1)
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)
        self.assertFalse(company.deleted)

        _company = Company.objects.get(company.id)
        self.assertEqual(_company.id, 1)
        self.assertEqual(_company.type, 'company')
        self.assertEqual(_company.name, 'test')
        self.assertEqual(_company.tags, ['1', '2', 'frog'])
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)
        self.assertFalse(_company.deleted)

    @amomock.activate
    def test_lead_create(self):
        statuses = copy.deepcopy(Lead.objects.leads_statuses)
        status = statuses.pop()
        lead = Lead(name='test', status=status['name'], price=10000.00)
        self.assertEqual(lead.name, 'test')
        self.assertEqual(lead.status, 'test')
        self.assertEqual(lead.price, 10000)
        self.assertIsNone(lead.id)

        lead.save()
        self.assertEqual(lead.name, 'test')
        self.assertEqual(lead.status, 'test')
        self.assertEqual(lead.price, 10000)
        self.assertEqual(lead.id, 1)
        
        _lead = Lead.objects.get(lead.id)
        self.assertEqual(_lead.name, 'test')
        self.assertEqual(_lead.status, 'test')
        self.assertEqual(_lead.price, 10000)
        self.assertEqual(_lead.id, 1)

    @amomock.activate
    def test_contact_task_create(self):
        contact = Contact(name='test')
        contact.save()

        statuses = copy.deepcopy(Contact.objects.task_types)
        status = statuses.pop()

        task = ContactTask(contact=contact, text='test task text', type=status['name'])
        self.assertEqual(task.contact.name, 'test')
        self.assertEqual(task.contact.id, contact.id)
        self.assertEqual(task.text, 'test task text')

        task.save()
        self.assertEqual(task.contact.name, 'test')
        self.assertEqual(task.contact.id, contact.id)
        self.assertEqual(task.text, 'test task text')

        _task = ContactTask.objects.get(task.id)
        self.assertEqual(_task.contact.name, 'test')
        self.assertEqual(_task.contact.id, contact.id)
        self.assertEqual(_task.text, 'test task text')
        self.assertEqual(_task._element_type, ContactTask.ELEMENT_TYPES['contact'])

    @amomock.activate
    def test_lead_task_create(self):
        lead = Lead(name='test')
        lead.save()

        task = LeadTask(lead=lead, text='test task text')
        self.assertEqual(task.lead.name, 'test')
        self.assertEqual(task.lead.id, lead.id)
        self.assertEqual(task.text, 'test task text')

        task.save()
        self.assertEqual(task.lead.name, 'test')
        self.assertEqual(task.lead.id, lead.id)
        self.assertEqual(task.text, 'test task text')

        _task = LeadTask.objects.get(task.id)
        self.assertEqual(_task.lead.name, 'test')
        self.assertEqual(_task.lead.id, lead.id)
        self.assertEqual(_task.text, 'test task text')
        self.assertEqual(_task._element_type, LeadTask.ELEMENT_TYPES['lead'])


class TestContacts(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    create_param = dict(name='test_name', deleted=False, tags=['1', '2', '3'], created_user=731)
    object_type = Contact

    @amomock.activate
    def test_getting_contact_by_id_and_data(self):
        self.create_object()
        contact = Contact.objects.get(1)

        self.assertEqual(contact.name, 'test_name')
        self.assertEqual(contact.id, 1)
        self.assertEquals(contact.deleted, False)
        self.assertSetEqual(set(contact.tags), set(['1', '2', '3']))
        self.assertEquals(contact.date_create.date(), from_ts(int(time.time())).date())
        self.assertEquals(contact.last_modified.date(), from_ts(int(time.time())).date())

        self.assertEquals(contact.created_user, 731)

    @amomock.activate
    def test_searching_contact(self):
        self.create_object()
        self.create_object(name='super_uniq')
        contact = Contact.objects.search('super_uniq')
        self.assertEqual(contact.name, 'super_uniq')

    @amomock.activate
    def test_edit_contact(self):
        self.create_object()
        contact = Contact.objects.get(1)
        self.assertNotEqual(contact.name, 'frog')
        contact.name = 'frog'
        contact.save()

        _contact = Contact.objects.get(1)
        self.assertEqual(_contact.name, 'frog')

    @amomock.activate
    def test_creating_tags(self):
        self.create_object(tags=['Tag2', 'Tag1'])

        _contact = Contact.objects.search('test_name')
        self.assertEqual(_contact.tags, ['Tag2', 'Tag1'])

        _contact.tags += ['frog']
        _contact.save()
        _contact = Contact.objects.search('test_name')
        self.assertEqual(_contact.tags, ['Tag2', 'Tag1', 'frog'])

    @amomock.activate
    def test_creating_company_by_contact(self):
        contact = self.create_object(company='testCo')
        contact.save()

        company = Company.objects.search('testCo')
        self.assertEqual(company.name, 'testCo')

    @amomock.activate
    def test_company_fk(self):
        contact = self.create_object(company='testCo')
        self.assertEquals(contact.company.name, 'testCo')
        self.assertEquals(contact.company.id, 1)

    @amomock.activate
    def test_edit_company_at_contact(self):
        contact = self.create_object(company='testCo')
        contact.company.name = 'SomeName'
        self.assertEquals(contact.company.name, 'SomeName')
        self.assertEquals(contact.company.id, 1)

        contact.company.name = 'Frog'
        contact.save()

        contact = Contact.objects.search('test_name')
        self.assertEquals(contact.company.name, 'Frog')
        self.assertEquals(contact.company.id, 1)


class TestCompany(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = Company
    create_param = {'name': 'test_name'}

    @amomock.activate
    def test_getting_company_by_id_and_data(self):
        self.create_object()
        company = self.object_type.objects.get(1)

        self.assertEqual(company.name, 'test_name')
        self.assertEqual(company.id, 1)
        self.assertEquals(company.deleted, False)
        self.assertEquals(company.date_create.date(), from_ts(int(time.time())).date())
        self.assertEquals(company.last_modified.date(), from_ts(int(time.time())).date())

    @amomock.activate
    def test_searching_company(self):
        self.create_object()
        self.create_object(name='super_uniq')
        company = self.object_type.objects.search('super_uniq')
        self.assertEqual(company.name, 'super_uniq')

    @amomock.activate
    def test_edit_company(self):
        self.create_object()
        company = self.object_type.objects.get(1)
        self.assertNotEqual(company.name, 'frog')
        company.name = 'frog'
        company.save()

        _company = self.object_type.objects.get(1)
        self.assertEqual(_company.name, 'frog')


class TestTask(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = ContactTask
    create_param = {'name': 'test_name'}

    @amomock.activate
    def test_getting_task_by_id_and_data(self):
        self.create_object(contact=self.create_object(object=Contact), text='TEST TEST')
        task = self.object_type.objects.get(1)

        self.assertEqual(task.name, 'test_name')
        self.assertEqual(task.id, 1)
        self.assertEqual(task.text, 'TEST TEST')
        self.assertEquals(task.deleted, False)
        self.assertEquals(task.date_create.date(), from_ts(int(time.time())).date())
        self.assertEquals(task.last_modified.date(), from_ts(int(time.time())).date())
        self.assertEquals(task.contact.name, 'test_name')
        self.assertEquals(task.contact.id, 1)

    @amomock.activate
    def test_searching_task(self):
        pass  # TODO: Tasks have not search ability

    @amomock.activate
    def test_edit_task(self):
        self.create_object()
        task = self.object_type.objects.get(1)
        self.assertNotEqual(task.name, 'frog')
        task.name = 'frog'
        task.save()

        _task = self.object_type.objects.get(1)
        self.assertEqual(_task.name, 'frog')


class TestLead(AmoSettingsMixin, CreateObjMixin, unittest.TestCase):
    object_type = Lead
    create_param = {'name': 'test_name', 'price': 100}

    @amomock.activate
    def test_getting_lead_by_id_and_data(self):
        self.create_object()
        lead = self.object_type.objects.get(1)

        self.assertEqual(lead.name, 'test_name')
        self.assertEqual(lead.id, 1)
        self.assertEquals(lead.deleted, False)
        self.assertEquals(lead.date_create.date(), from_ts(int(time.time())).date())
        self.assertEquals(lead.last_modified.date(), from_ts(int(time.time())).date())

    @amomock.activate
    def test_searching_lead(self):
        self.create_object()
        self.create_object(name='super_uniq', price=999)
        lead = self.object_type.objects.search('super_uniq')
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


if __name__ == '__main__':
    unittest.main()
