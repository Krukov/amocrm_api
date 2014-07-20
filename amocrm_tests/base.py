# -*- coding: utf-8 -*-

import time
from datetime import datetime

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

    # @amomock.activate
    # def test_edit_contact(self):
    #     contact = Contact.objects.get(0)
    #     self.assertNotEqual(contact.name, 'Frog')
    #     contact.name = 'frog'
    #     contact.save()

    #     _contact = Contact.objects.get(0)
    #     self.assertEqual(_contact.name, 'frog')

    # @amomock.activate
    # def test_creating_contact(self):
    #     contact = Contact(name='test', email='test@test.ru', company='TEST.CO')
    #     contact.save()

if __name__ == '__main__':
    unittest.main()
