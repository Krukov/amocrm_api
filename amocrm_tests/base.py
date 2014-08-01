# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from datetime import datetime

from amocrm import *
from amocrm_tests.utils import amomock


class TestContacts(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        amo_settings.set('test', 'test', 'testcentrobit')

    @amomock.activate
    def test_getting_contact_by_id_and_data(self):
        contact = Contact.objects.get(0)

        self.assertEqual(contact.name, 'Parker Crosby')
        self.assertEqual(contact.id, 0)
        self.assertEquals(contact.deleted, True)
        self.assertSetEqual(set(contact.tags.replace(', ', ',').split(',')), {'Hodges Watts', 'Carrillo Beach', 'Bonner Leon'})
        self.assertEquals(contact.date_create, datetime.fromtimestamp(67444200))
        self.assertEquals(contact.last_modified, datetime.fromtimestamp(7675716))

        self.assertEquals(contact.created_user, 731)
        self.assertEqual(contact.company.name, 'TWIIST')

    @amomock.activate
    def test_searching_contact(self):
        contact = Contact.objects.search('traceywalsh@voratak.com')
        self.assertEqual(contact.name, 'Tracey Walsh')

    @amomock.activate
    def test_edit_contact(self):
        contact = Contact.objects.get(0)
        self.assertNotEqual(contact.name, 'frog')
        contact.name = 'frog'
        contact.save()

        _contact = Contact.objects.get(0)
        self.assertEqual(_contact.name, 'frog')

    @amomock.activate
    def test_creating_tags(self):
        contact = Contact(name='TestTags', tags=['Tag2', 'Tag1'])
        self.assertEqual(contact.tags, 'Tag2, Tag1')
        contact.save()

        _contact = Contact.objects.search('TestTags')
        self.assertEqual(_contact.tags, 'Tag2, Tag1')

        _contact.tags += ', frog'
        _contact.tags

    @amomock.activate
    def test_creating_contact(self):
        contact = Contact(name='test', email='test@test.ru')
        self.assertEqual(contact.name, 'test')
        self.assertEqual(contact.email, 'test@test.ru')

        contact.save()

        _contact = Contact.objects.get(contact.id)
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.email, 'test@test.ru')
        self.assertEqual(_contact.date_create.date(), datetime.now().date())

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
    def test_creating_company(self):
        company = Company(name='test')
        company.save()

        _company = Company.objects.get(company.id)
        self.assertEqual(_company.name, 'test')



if __name__ == '__main__':
    unittest.main()
