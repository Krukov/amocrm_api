# -*- coding: utf-8 -*-

import time
from datetime import datetime

import unittest

import amocrm
from amocrm.decorators import empty
from amocrm import fields


class FieldsTests(unittest.TestCase):

    def test_constant_field(self):
        f = fields.ConstantField('test', 'value')
        self.assertEqual(f.field, 'test')
        self.assertEqual(f.data, 'value')

    def test_datetime_field(self):
        f = fields.DateTimeField('test')
        self.assertEqual(f.field, 'test')
        f.data = time.time()
        self.assertEqual(f.data, datetime.now())

    def test_bool_field(self):
        f = fields.BooleanField('test')
        self.assertEqual(f.field, 'test')
        f.data = '1'
        self.assertTrue(f.data)
        f.data = 'Yes'
        self.assertTrue(f.data)
        f.data = 0
        self.assertFalse(f.data)
        f.data = '0'
        self.assertFalse(f.data)

    def test_foreign_field(self):
        f = fields.ForeignField(amocrm.Contact, 'test', ['name', 'two'])
        self.assertEqual(f.field, 'test')
        self.assertEqual(f._keys, ['name', 'two'])
        self.assertEqual(f.object_type, amocrm.Contact)
        f._keys_data = {'name': 'test_'}
        f.data = 1
        self.assertEqual(f.data.name, 'test_')
        self.assertIsInstance(f.data, empty)

    def test_many_dict_field(self):
        f = fields.ManyDictField('test', 'name')
        self.assertEqual(f.field, 'test')
        f.data = [{'foreign': 1, 'id': 100, 'name': 'frog'},
                  {'foreign': 2, 'id': 200, 'name': 'test'},]

        self.assertEqual(f.data['frog'].id, 100)
        self.assertEqual(f.data['test'].foreign, 2)
        self.assertEqual(f.data['frog'].name, 'frog')

    def test_many_f_field(self):
        f = fields.ManyForeignField(amocrm.Contact, 'test')
        self.assertEqual(f.field, 'test')
        f.data = [1, 4, 10]
        self.assertIsInstance(f.data[0], empty)
        self.assertEqual(len(f.data), 3)


