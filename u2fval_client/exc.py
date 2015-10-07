# Copyright (c) 2014 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__all__ = [
    'U2fValClientException',
    'ServerUnreachableException',
    'BadAuthException',
    'U2fValException',
    'BadInputException',
    'NoEligableDevicesException',
    'DeviceCompromisedException',
    'from_response'
]


class U2fValClientException(Exception):

    "Exception generated on the client"


class ServerUnreachableException(U2fValClientException):

    "The U2FVAL server cannot be reached"


class InvalidResponseException(U2fValClientException):

    "The server sent something which is not valid"


class BadAuthException(U2fValClientException):

    "Access was denied"


class U2fValException(Exception):

    "Exception sent from the U2FVAL server"

    def __init__(self, message, data=None):
        super(U2fValException, self).__init__(message, data)

        self.message = message
        self.data = data


class BadInputException(U2fValException):

    "The arguments passed to the function are invalid"
    code = 10


class NoEligableDevicesException(U2fValException):

    "The user has no eligable devices capable of the requested action"
    code = 11

    def has_devices(self):
        return bool(self.data)


class DeviceCompromisedException(U2fValException):

    "The device might be compromised, and has been blocked"
    code = 12


_ERRORS = {
    10: BadInputException,
    11: NoEligableDevicesException,
    12: DeviceCompromisedException,
    401: BadAuthException
}


def from_response(response):
    error_cls = _ERRORS.get(response['errorCode'], U2fValException)
    return error_cls(response.get('errorMessage'), response.get('errorData'))
