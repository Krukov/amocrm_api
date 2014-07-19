# -*- coding: utf-8 -*-
# swagger
import unittest
import json
import requests

from utils import amomock


class TestUtils(unittest.TestCase):
    login_data = {'USER_LOGIN': 'test', 'USER_HASH': 'test'}

    def setUp(self):
        amomock.set_login_params('test', 'test')

    @amomock.activate
    def test_auth_request(self):
        resp = requests.post('http://test.amocrm/private/api/auth.php',
                             data=self.login_data)
        self.assertEquals(resp.json()['auth'], True)

    @amomock.activate
    def test_invalid_login(self):
        resp = requests.post('http://test.amocrm/private/api/auth.php',
                             {'USER_LOGIN': 'test', 'USER_HASH': 'test2'})
        self.assertEquals(resp.json()['auth'], False)

    @amomock.activate
    def test_current_getting(self):
        resp = requests.get('http://test.amocrm/private/api/accounts/current',
                            data=self.login_data).json()
        self.assertNotIn('auth', resp)
        self.assertIn('response', resp)
        info = resp['response']['accounts']
        self.assertIn('id', info)
        self.assertIn('users', info)
        self.assertIn('id', info['users'].pop())
        self.assertIn('custom_fields', info)

    @amomock.activate
    def test_contacts_getting(self):
        data = {'request': json.dumps({'contacts': {'limit_rows': 2}})}
        data.update(self.login_data)
        resp = requests.get('http://test.amocrm/private/api/contacts/list',
                            data=data).json()
        self.assertNotIn('auth', resp)
        self.assertIn('response', resp)
        contacts = resp['response']['contacts']
        self.assertEquals(len(contacts), 2)
        self.assertIn('id', contacts.pop())

    @amomock.activate
    def test_contacts_search(self):
        data = {'request': json.dumps({'contacts': {'limit_rows': 1, 'query': {'name': 'Molina Chapman'}}})}
        data.update(self.login_data)
        resp = requests.get('http://test.amocrm/private/api/contacts/list',
                            data=data).json()
        self.assertNotIn('auth', resp)
        self.assertIn('response', resp)
        contacts = resp['response']['contacts']
        self.assertEquals(len(contacts), 1)
        self.assertEquals('Molina Chapman', contacts.pop()['name'])


if __name__ == '__main__':
    unittest.main()
