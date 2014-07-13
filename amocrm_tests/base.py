# -*- coding: utf-8 -*-

import time
from datetime import datetime

import unittest

from amocrm import *
from amocrm.decorators import empty


class TestContacts(unittest.TestCase):

    def setUp(self):
        settings.set()
    
    def test_getting_contact_by_id(self):
        contact = Contact.objects.get(1)

    def test_searching_contact(self):
        contact = Contact.objects.search('test@test.ru')

    def test_edit_contact(self):
        contact = Contact.objects.get(1)
        assert contact.name != 'frog'
        contact.name = 'frog'
        contact.save()

        _contact = Contact.objects.get(1)
        self.assertEqual(_contact.name, 'frog')

    def test_creating_contact(self):
        contact = Contact({
                'name': 'test',
                'email': 'test@test.ru',
                'company': 'TEST.CO'
            })
        contact.save()

if __name__ == '__main__':
    unittest.main()
