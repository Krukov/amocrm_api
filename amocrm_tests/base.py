# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

from amocrm.apimodels import *
from amocrm_tests.utils import amomock


class TestContacts(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        settings.set('test', 'test', 'testcentrobit')

    @amomock.activate
    def test_getting_contact_by_id_and_data(self):
        contact = Contact.objects.get(0)

        self.assertEqual(contact.name, 'Parker Crosby')
        self.assertEqual(contact.id, 0)
        self.assertEquals(contact.deleted, True)
        self.assertEquals(contact.tags[1].name, 'Carrillo Beach')
        self.assertEquals(contact.datecreate, datetime.fromtimestamp(67444200))
        self.assertEquals(contact.last_modified, datetime.fromtimestamp(7675716))

        self.assertEquals(contact.created_user, '731')


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
    def test_creating_contact(self):
        contact = Contact(name='test', email='test@test.ru')
        _id = contact.save()

        _contact = Contact.objects.get(_id['id'])
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.email, 'test@test.ru')

    @amomock.activate
    def test_creating_company(self):
        company = Company(name='test', adress='test@test.ru')
        _id = company.save()

        _company = Company.objects.get(_id['id'])
        self.assertEqual(_company.name, 'test')
        self.assertEqual(_contact.adress, 'test@test.ru')

    @amomock.activate
    def test_creating_company_by_contact(self):
        contact = Contact(name='test', email='test@test.ru', company='testCo')
        contact.save()

        company = Company.objects.search({'name': 'testCo'})
        self.assertEqual(company.name, 'testCo')

    @amomock.activate
    def test_company_fk(self):
        contact = Contact(name='test', email='test@test.ru', company='testCo')
        contact.save()
        self.assertEquals(contact.company.name, 'testCo')
        self.assertEquals(contact.company.id, 4)

if __name__ == '__main__':
    unittest.main()
