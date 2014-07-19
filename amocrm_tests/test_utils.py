# -*- coding: utf-8 -*-

import unittest
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
        resp = requests.get('http://test.amocrm/private/api/accounts/current', data=self.login_data).json()
        self.assertNotIn('auth', resp)
        self.assertIn('id', resp)
