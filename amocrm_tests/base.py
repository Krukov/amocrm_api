# -*- coding: utf-8 -*-

import unittest

from amocrm import *
from amocrm.decorators import empty
from amocrm_tests.utils import amomock


class TestContacts(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')
        settings.set('test', 'test', 'testcentrobit')

    @amomock.activate
    def test_getting_contact_by_id(self):
        contact = Contact.objects.get(0)
        self.assertEqual(contact.name, 'Parker Crosby')

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
        contact = Contact(name='test', email='test@test.ru', company='TEST.CO')
        _id = contact.save()

        _contact = Contact.objects.get(_id['id'])
        self.assertEqual(_contact.name, 'test')
        self.assertEqual(_contact.email, 'test@test.ru')
        # self.assertEqual(_contact.company, 'TEST.CO')


if __name__ == '__main__':
    unittest.main()
