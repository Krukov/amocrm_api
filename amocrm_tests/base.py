# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from datetime import datetime

from amocrm import *
from amocrm_tests.utils import amomock

from_ts = datetime.fromtimestamp


class TestCreations(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        amo_settings.set('test', 'test', 'test')

    @amomock.activate
    def test_creating_contact(self):
        contact = Contact(name='test', tags=['1', '2', 'frog'])
        self.assertIsNone(contact.id)
        self.assertEqual(contact.type, 'contact')
        self.assertEqual(contact.name, 'test')
        self.assertEqual(contact.tags, '1, 2, frog')
        self.assertIsNone(contact.date_create)
        self.assertIsNone(contact.last_modified)
        self.assertIsNone(contact.rui)

        contact.save()
        self.assertEqual(contact.id, 1)
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)

        _contact = Contact.objects.get(contact.id)
        self.assertEqual(_contact.id, 1)
        self.assertEqual(_contact.type, 'contact')
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.tags, '1, 2, frog')
        self.assertIsNotNone(contact.last_modified)
        self.assertIsNotNone(contact.date_create)
        self.assertEqual(_contact.date_create.date(), datetime.now().date())
        self.assertEqual(_contact.rui, '99')


    @amomock.activate
    def test_creating_company(self):
        company = Company(name='test', tags=['1', '2', 'frog'])
        self.assertIsNone(company.id)
        self.assertEqual(company.type, 'company')
        self.assertEqual(company.name, 'test')
        self.assertEqual(company.tags, '1, 2, frog')
        self.assertIsNone(company.last_modified)
        self.assertIsNone(company.date_create)

        company.save()
        self.assertEqual(company.id, 1)
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)

        _company = Company.objects.get(company.id)
        self.assertEqual(_company.id, 1)
        self.assertEqual(_company.type, 'company')
        self.assertEqual(_company.name, 'test')
        self.assertEqual(_company.tags, '1, 2, frog')
        self.assertIsNotNone(company.last_modified)
        self.assertIsNotNone(company.date_create)


class TestContacts(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        amo_settings.set('test', 'test', 'testcentrobit')

    @amomock.activate
    def test_creating_contact(self):
        contact = Contact(name='test')
        self.assertEqual(contact.name, 'test')

        contact.save()

        _contact = Contact.objects.get(contact.id)
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.date_create.date(), datetime.now().date())

    def create_contact(self, **kwargs):
        kw = dict(name='test_name', deleted=False, tags=['1', '2', '3'], created_user=731)
        kw.update(**kwargs)
        Contact(**kw).save()

    @amomock.activate
    def test_getting_contact_by_id_and_data(self):
        self.create_contact()
        contact = Contact.objects.get(1)

        self.assertEqual(contact.name, 'test_name')
        self.assertEqual(contact.id, 1)
        self.assertEquals(contact.deleted, False)
        self.assertSetEqual(set(contact.tags.replace(', ', ',').split(',')),
                            {'1', '2', '3'})
        self.assertEquals(contact.date_create.date(), from_ts(int(time.time())).date())
        self.assertEquals(contact.last_modified.date(), from_ts(int(time.time())).date())

        self.assertEquals(contact.created_user, 731)

    @amomock.activate
    def test_searching_contact(self):
        self.create_contact()
        self.create_contact(name='super_uniq')
        contact = Contact.objects.search('super_uniq')
        self.assertEqual(contact.name, 'super_uniq')

    @amomock.activate
    def test_edit_contact(self):
        self.create_contact()
        contact = Contact.objects.get(1)
        self.assertNotEqual(contact.name, 'frog')
        contact.name = 'frog'
        contact.save()

        _contact = Contact.objects.get(1)
        self.assertEqual(_contact.name, 'frog')

    @amomock.activate
    def test_creating_tags(self):
        contact = Contact(name='TestTags', tags=['Tag2', 'Tag1'])
        self.assertEqual(contact.tags, 'Tag2, Tag1')
        contact.save()

        _contact = Contact.objects.search('TestTags')
        self.assertEqual(_contact.tags, 'Tag2, Tag1')

        _contact.tags += ', frog'
        _contact.save()
        _contact = Contact.objects.search('TestTags')
        self.assertEqual(_contact.tags, 'Tag2, Tag1, frog')

    @amomock.activate
    def test_creating_company_by_contact(self):
        contact = Contact(name='test', email='test@test.ru', company='testCo')
        contact.save()

        company = Company.objects.search('testCo')
        self.assertEqual(company.name, 'testCo')

    @amomock.activate
    def test_company_fk(self):
        contact = Contact(name='test', email='test@test.ru', company='testCo')
        contact.save()
        self.assertEquals(contact.company.name, 'testCo')
        self.assertEquals(contact.company.id, 1)

    @amomock.activate
    def test_edit_company_at_contact(self):
        contact = Contact(name='test', email='test@test.ru', company='testCo')
        contact.company.name = 'SomeName'
        contact.save()

        self.assertEquals(contact.company.name, 'SomeName')
        self.assertEquals(contact.company.id, 1)

        contact.company.name = 'Frog'
        contact.save()

        contact = Contact.objects.search('test')
        self.assertEquals(contact.company.name, 'Frog')
        self.assertEquals(contact.company.id, 1)

    ## TESTS COMPANY API
    @amomock.activate
    def test_editing_company(self):
        pass

if __name__ == '__main__':
    unittest.main()
