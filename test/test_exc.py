import unittest

from u2fval_client.exc import (
    BadAuthException,
    BadInputException,
    DeviceCompromisedException,
    NoEligableDevicesException,
    U2fValException,
    from_response,
)


class TestU2fValException(unittest.TestCase):
    def test_message_only(self):
        self.assertEqual(U2fValException("It's dead").message, "It's dead")

    def test_message_and_data(self):
        self.assertEqual(U2fValException("It's dead", "Nailed to perch").data, "Nailed to perch")


class TestNoEligableDevicesException(unittest.TestCase):
    def test_has_devices_message_only(self):
        self.assertFalse(NoEligableDevicesException("It's dead").has_devices())

    def test_has_devices_with_data(self):
        self.assertFalse(NoEligableDevicesException("It's dead", False).has_devices())
        self.assertTrue(NoEligableDevicesException("It's dead", True).has_devices())


class TestFromResponse(unittest.TestCase):

    def test_known_errorcode(self):
        self.assertIsInstance(from_response({'errorCode': 10}), BadInputException)
        self.assertIsInstance(from_response({'errorCode': 11}), NoEligableDevicesException)
        self.assertIsInstance(from_response({'errorCode': 12}), DeviceCompromisedException)
        self.assertIsInstance(from_response({'errorCode': 401}), BadAuthException)

    def test_unknown_errorcode(self):
        self.assertIsInstance(from_response({'errorCode': 0xdeadbeef}), U2fValException)

    def test_error_message(self):
        exc = from_response({'errorCode': 10, 'errorMessage': "It's dead"})
        self.assertEqual(exc.message, "It's dead")
        self.assertIsNone(exc.data)

    def test_error_data(self):
        exc = from_response({'errorCode': 10, 'errorData': "Nailed to perch"})
        self.assertIsNone(exc.message)
        self.assertEqual(exc.data, "Nailed to perch")

