# -*- coding: utf-8 -*-

import unittest
import requests

from .TestUtils import amomock


class TestUtils(unittest.TestCase):

    def setUp(self):
        amomock.set_login_params('test', 'test')

    @amomock.activate
    def test_auth_request(self):
        resp = requests.post('http://test.amocrm/private/api/auth.php',
                      {'USER_LOGIN': 'test', 'USER_HASH': 'test'})
        self.assertEquals(resp.json()['auth'], 'true')

    @amomock.activate
    def test_unvalid_login(self):
        resp = requests.post('http://test.amocrm/private/api/auth.php',
                      {'USER_LOGIN': 'test', 'USER_HASH': 'test2'})
        self.assertEquals(resp.json()['auth'], 'false')
