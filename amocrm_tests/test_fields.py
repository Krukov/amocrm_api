# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
import time
from datetime import datetime, timedelta

from amocrm import fields
from amocrm.test_utils import amomock


class TestBaseFields(unittest.TestCase):

    def setUp(self):
        self.data = {
            'field': 'test_field',
            'uneditable': 'test_uneditable',
            'constant': 'test_constant',
            'bool': 1,
            'datetime': time.time(),
            'tags': '1, 3 5, frog',
            'custom_fields': [
                {'id': 1, 'values': [{'enum': '_TEST_', 'value': 'test_field_1'}]},
                {'id': 2, 'values': [{'value': 'test_field_2'}]},
                {'id': 3, 'values': [
                    {'enum': 'TEST', 'value': '1_test_field_3'},
                    {'enum': 'TEST2', 'value': '2_test_field_3'}
                ]},
            ],
        }

        class TestClass(object):
            field = fields._Field('field')
            uneditable = fields._UneditableField('uneditable')
            constant = fields._ConstantField('constant', 'test_constant')
            datetime = fields._DateTimeField('datetime')
            bool = fields._BooleanField('bool')
            tags = fields._TagsField('tags')

            def __init__(self, data):
                self._data = data
                self._fields_data = {}
                self._changed_fields = []

        self.instance = TestClass(data=self.data)

    def test_fields(self):

        self.assertEqual(self.instance.field, self.data['field'])
        self.assertEqual(self.instance.uneditable, self.data['uneditable'])
        self.assertEqual(self.instance.constant, self.data['constant'])
        self.assertEqual(self.instance.bool, bool(self.data['bool']))
        self.assertEqual(self.instance.datetime, datetime.utcfromtimestamp(self.data['datetime']))
        self.assertEqual(self.instance.tags, self.data['tags'].replace(', ', ',').split(','))

        self.instance.field = 'new_field'
        self.instance.bool = 0
        new_date = datetime.utcnow() - timedelta(days=1)
        self.instance.datetime = new_date
        self.instance.tags = ['new', 'test']

        self.assertEqual(self.instance.field, self.data['field'])
        self.assertEqual(self.instance.uneditable, self.data['uneditable'])
        self.assertEqual(self.instance.constant, self.data['constant'])
        self.assertEqual(self.instance.bool, False)
        self.assertEqual(self.instance.datetime, datetime.utcfromtimestamp(self.data['datetime']))
        self.assertEqual(self.instance.tags, ['new', 'test'])

