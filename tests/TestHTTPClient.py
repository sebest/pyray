#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TestHTTPClient
----------------------------------

Tests for `pyray` module.
"""

import unittest
import responses
from pyray import client
from pyray import exceptions

def assert_reset():
    """
    Reset mock responses
    """
    assert len(responses._default_mock._urls) == 0
    assert len(responses.calls) == 0

class TestHTTPClient(unittest.TestCase):

    def test_correct_login(self):
        """
        Given a 200 response, make sure the HTTPClient
        attribute logged_in is True
        """

        @responses.activate
        def run():
            responses.add(responses.GET, 'https://dev-api:9070/api/tm/2.0',
                          body='{"children":[]}', status=200,
                          content_type='application/json')
            self.assertTrue(client.HTTPClient(service_url='dev-api',
                                              username='user1',
                                              password='pass123').logged_in)

        run()
        assert_reset()

    def test_incorrect_login(self):
        """
        Given a 401 response, make sure HTTPClient
        raises AuthorizationFailure.
        """
        @responses.activate
        def run():
            responses.add(responses.GET, 'https://dev-api:9070/api/tm/2.0',
                          body='{"children":[]}', status=401,
                          content_type='application/json')
            self.assertRaises(exceptions.AuthorizationFailure,
                              client.HTTPClient,
                              service_url='dev-api',
                              username='user1',
                              password='pass1234')

        run()
        assert_reset()

if __name__ == '__main__':
    unittest.main()