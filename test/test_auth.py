import unittest

from u2fval_client.auth import (
    ApiToken,
    HttpAuth,
    no_auth,
)


class TestNoAuth(unittest.TestCase):
    def test_no_auth(self):
        self.assertEqual(no_auth({}), {})
        self.assertEqual(no_auth({'foo': 'bar'}), {'foo': 'bar'})


class TestApiToken(unittest.TestCase):
    def setUp(self):
        self.api_token = ApiToken('abc123')

    def test_call_headers_empty(self):
        self.assertEqual(self.api_token({}),
                         {'headers': {'Authorization': 'Bearer abc123'}})

    def test_call_headers_present(self):
        self.assertEqual(self.api_token({'headers': {'foo': 'bar'}}),
                         {'headers': {'Authorization': 'Bearer abc123',
                                      'foo': 'bar'}})


class TestHttpAuth(unittest.TestCase):
    def test_without_authtype(self):
        http_auth = HttpAuth('black_knight', 'Just a flesh wound!')
        self.assertEqual(http_auth({}),
                         {'auth': ('black_knight', 'Just a flesh wound!')})

