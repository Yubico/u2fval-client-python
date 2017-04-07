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

    def __init__(self, endpoint, auth=auth.no_auth, extra_args={}):
        if endpoint[-1] != '/':
            endpoint = endpoint + '/'
        self._endpoint = endpoint
        self._auth = auth
        self._extra_args = extra_args

    def _req(self, method, url, json=None, resp_is_json=True, **kwargs):
        args = dict(self._extra_args)
        args.update(kwargs)
        args = self._auth(args)
        if json is not None:
            headers = args.get('headers', {})
            headers['Content-type'] = 'application/json'
            args['headers'] = headers
            args['data'] = _json.dumps(json)

        status = -1
        try:
            resp = requests.request(method, url, **args)
            status = resp.status_code
            if status < 400:
                return resp.json() if resp_is_json else resp.content
            else:
                raise exc.from_response(resp.json())
        except requests.ConnectionError as e:
            raise exc.ServerUnreachableException(str(e))
        except ValueError:
            if status == 401:
                raise exc.BadAuthException('Access denied')
            elif status == 404:
                raise exc.U2fValClientException('Not found')
            else:
                raise exc.InvalidResponseException(
                    'The server responded with invalid data')

    def get_trusted_facets(self):
        return self._req('GET', self._endpoint)

    def get_device(self, username, handle):
        url = self._endpoint + username + '/' + handle
        return self._req('GET', url)

    def get_certificate(self, username, handle):
        url = self._endpoint + username + '/' + handle
        return self._req('GET', url, resp_is_json=False)

    def delete_user(self, username):
        url = self._endpoint + username + '/'
        self._req('DELETE', url, resp_is_json=False)

    def list_devices(self, username):
        url = self._endpoint + username + '/'
        return self._req('GET', url)

    def update_device(self, username, handle, properties):
        url = self._endpoint + username + '/' + handle
        return self._req('POST', url, json=properties)

    def register_begin(self, username, properties=None, challenge=None):
        url = self._endpoint + username + '/register'
        params = {}
        if properties is not None:
            params['properties'] = _json.dumps(properties)
        if challenge is not None:
            params['challenge'] = challenge
        return self._req('GET', url, params=params)

    def register_complete(self, username, register_response, properties=None):
        url = self._endpoint + username + '/register'
        data = {'registerResponse': _json.loads(register_response)}
        if properties:
            data['properties'] = properties

        return self._req('POST', url, json=data)

    def unregister(self, username, handle):
        url = self._endpoint + username + '/' + handle
        self._req('DELETE', url, resp_is_json=False)

    def auth_begin(self, username, properties=None, challenge=None,
                   handles=None):
        url = self._endpoint + username + '/sign'
        params = {}
        if properties is not None:
            params['properties'] = _json.dumps(properties)
        if challenge is not None:
            params['challenge'] = challenge
        if handles is not None:
            params['handle'] = handles
        return self._req('GET', url, params=params)

    def auth_complete(self, username, sign_response, properties=None):
        url = self._endpoint + username + '/sign'
        data = {'signResponse': _json.loads(sign_response)}
        if properties:
            data['properties'] = properties
        return self._req('POST', url, json=data)
