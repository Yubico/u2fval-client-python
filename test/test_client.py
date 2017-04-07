import unittest

import httpretty

from u2fval_client.client import (
    Client,
)
from u2fval_client.exc import (
    BadAuthException,
    BadInputException,
    ServerUnreachableException,
    InvalidResponseException,
    U2fValClientException,
)


@httpretty.activate
class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client('https://example')

    def test_endpoint_sanitised(self):
        self.assertEqual('https://example/', self.client._endpoint)

    def test_get_trusted_facets(self):
        httpretty.register_uri('GET', 'https://example/',
                               body='{}')
        self.assertEqual(self.client.get_trusted_facets(), {})

    def test_get_trusted_facets_empty_response_body(self):
        httpretty.register_uri('GET', 'https://example/',
                               body='')
        self.assertRaises(InvalidResponseException,
                          self.client.get_trusted_facets)

    def test_get_trusted_facets_error_code(self):
        httpretty.register_uri('GET', 'https://example/',
                               body='{"errorCode": 10}',
                               status=400)
        self.assertRaises(BadInputException, self.client.get_trusted_facets)

    def test_get_trusted_facets_unauthorized(self):
        httpretty.register_uri('GET', 'https://example/', status=401)
        self.assertRaises(BadAuthException, self.client.get_trusted_facets)

    def test_get_trusted_facets_not_found(self):
        httpretty.register_uri('GET', 'https://example/', status=404)
        self.assertRaises(U2fValClientException, self.client.get_trusted_facets)

    def test_get_trusted_facets_internal_server_error(self):
        httpretty.register_uri('GET', 'https://example/', status=500)
        self.assertRaises(U2fValClientException, self.client.get_trusted_facets)

    def test_get_trusted_facets_server_unreachable(self):
        # Intentionally has no httpretty mock registered
        self.assertRaises(ServerUnreachableException,
                          self.client.get_trusted_facets)

    def test_list_devices(self):
        httpretty.register_uri('GET', 'https://example/black_knight/',
                               body='{}')
        self.assertEqual(self.client.list_devices('black_knight'), {})

    def test_register_begin(self):
        httpretty.register_uri('GET', 'https://example/black_knight/register',
                               body='{}')
        self.assertEqual(self.client.register_begin('black_knight'), {})

    def test_register_complete(self):
        httpretty.register_uri('POST', 'https://example/black_knight/register',
                               body='{}')
        self.assertEqual(self.client.register_complete('black_knight', '{}'),
                         {})
        req = httpretty.last_request()
        self.assertEqual(req.parsed_body, {'registerResponse': {}})

    def test_unregister(self):
        httpretty.register_uri('DELETE', 'https://example/black_knight/abc123',
                               body='', status=204)
        self.assertIsNone(self.client.unregister('black_knight', 'abc123'))

    def test_auth_begin(self):
        httpretty.register_uri('GET', 'https://example/black_knight/sign',
                               body='{}')
        self.assertEqual(self.client.auth_begin('black_knight'), {})

    def test_auth_complete(self):
        httpretty.register_uri('POST', 'https://example/black_knight/sign',
                               body='{}')
        self.assertEqual(self.client.auth_complete('black_knight', '{}'), {})
        req = httpretty.last_request()
        self.assertEqual(req.parsed_body, {'signResponse': {}})
