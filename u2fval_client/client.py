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

from u2fval_client import auth, exc
import requests
import json as _json


class Client(object):

    def __init__(self, endpoint, auth=auth.no_auth):
        if endpoint[-1] != '/':
            endpoint = endpoint + '/'
        self._endpoint = endpoint
        self._auth = auth

    def _req(self, method, url, json=None, **kwargs):
        kwargs = self._auth(kwargs)
        if json is not None:
            headers = kwargs.get('headers', {})
            headers['Content-type'] = 'application/json'
            kwargs['headers'] = headers
            kwargs['data'] = _json.dumps(json)
        try:
            resp = requests.request(method, url, **kwargs)
            status = resp.status_code
            try:
                data = resp.json()
            except ValueError:
                data = {}
            if 'errorCode' in data:
                raise exc.from_response(data)
            if status < 400:
                return data
            elif status == 401:
                raise exc.BadAuthException('Access denied')
            elif status == 404:
                raise exc.U2fValClientException('Not found')
            else:
                raise exc.U2fValClientException('Unknown error')
        except requests.ConnectionError as e:
            raise exc.ServerUnreachableException(e.message)

    def get_trusted_facets(self):
        return self._req('GET', self._endpoint)

    def list_devices(self, username):
        url = self._endpoint + username + '/'
        return self._req('GET', url)

    def register_begin(self, username):
        url = self._endpoint + username + '/register'
        return self._req('GET', url)

    def register_complete(self, username, register_response, properties=None):
        url = self._endpoint + username + '/register'
        data = {'registerResponse': _json.loads(register_response)}
        if properties:
            data['properties'] = properties

        return self._req('POST', url, json=data)

    def unregister(self, username, handle):
        url = self._endpoint + username + '/' + handle
        return self._req('DELETE', url)

    def auth_begin(self, username):
        url = self._endpoint + username + '/authenticate'
        return self._req('GET', url)

    def auth_complete(self, username, authenticate_response, properties=None):
        url = self._endpoint + username + '/authenticate'
        data = {'authenticateResponse': _json.loads(authenticate_response)}
        if properties:
            data['properties'] = properties
        return self._req('POST', url, json=data)
