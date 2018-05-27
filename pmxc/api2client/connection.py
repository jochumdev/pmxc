import logging
import urllib.parse

import aiohttp

from pmxc.api2client.exception import AuthenticationException
from pmxc.api2client.exception import ConnectionException
from pmxc.api2client.exception import HTTPException
from pmxc.api2client.exception import VerifyException
from pmxc.api2client.resource import Resource


__all__ = [
    'Connection',
]


def _hex_fp_to_binary(fp):
    return bytes.fromhex(''.join(fp.split(':')))


def _binary_fp_to_hex(fp):
    return ':'.join(['{0:02x}'.format(fp[i]) for i in range(0, len(fp))])


def _manual_verify_fp(host, _, hex_fp):
    res = input('''The authenticity of host '%s' can't be established.
X509 SHA256 key fingerprint is %s.
Are you sure you want to continue connecting (yes/no)? ''' % (host, hex_fp))
    if res.lower()[0] != 'y':
        return False

    return True


class Connection(object):
    def __init__(self, loop, host, *, port=None, fingerprint=None,
                 verify_cb=None):

        self._loop = loop
        self._host = host
        self._port = port if port is not None else 8006
        if fingerprint is not None:
            self._fingerprint = _hex_fp_to_binary(fingerprint)
        else:
            self._fingerprint = None
        self._verify_cb = verify_cb if verify_cb is not None else _manual_verify_fp

        self._timeout = 30

        self._ticket = None
        self._caps = None
        self._csrftoken = None

        self._url = 'https://' + host + ':' + str(port)

    @property
    def fingerprint(self):
        return _binary_fp_to_hex(self._fingerprint) if self._fingerprint is not None else None

    @property
    def binary_fingerprint(self):
        return self._fingerprint

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def ticket(self):
        return self._ticket

    async def update_ticket(self, value):
        self._ticket = value

        # Reconnect with Ticket
        await self._close_connection()
        await self._make_connection()

    @property
    def caps(self):
        return self._caps

    @property
    def csrftoken(self):
        return self._csrftoken

    @property
    def url(self):
        return self._url

    @property
    def session(self):
        return self._session

    def url_join(self, *args):
        path = '/api2/json/' + '/'.join(args)
        return Resource(self, path)

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)

        return self.url_join(item)

    async def get(self, path, **params):
        json = await self.request('GET', path, **params)
        return json['data']

    async def post(self, path, **params):
        json = await self.request('POST', path, **params)
        return json['data']

    async def put(self, path, **params):
        json = await self.request('PUT', path, **params)
        return json['data']

    async def delete(self, path, **params):
        json = await self.request('DELETE', path, **params)
        return json['data']

    async def options(self, path, **params):
        json = await self.request('OPTIONS', path, **params)
        return json['data']

    async def request(self, method, path, **params):
        url = self._url + path

        data = aiohttp.FormData()
        for k, v in params.items():
            data.add_field(k, v)

        try:
            logging.debug('%s: %s', method, url)
            resp = await self._session.request(method, url, data=data, ssl=aiohttp.Fingerprint(self._fingerprint))
            if int(resp.status / 100) != 2:
                raise HTTPException(url, resp.status, resp.reason)
        except aiohttp.client_exceptions.ClientConnectorError as e:
            raise ConnectionException(e)

        return await resp.json()

    async def login(self, username, password=None, ticket=None):
        if password is None and ticket is None:
            raise ValueError('You need to give either a password or a cookie')

        assert self._session

        url = self._url + '/api2/json/access/ticket'

        data = aiohttp.FormData()
        data.add_field("username", username)
        data.add_field("password", password)
        resp = await self._session.post(url, data=data, ssl=aiohttp.Fingerprint(self._fingerprint))
        if int(resp.status / 100) != 2:
            raise AuthenticationException(url, resp.status, resp.reason)

        json = await resp.json()
        result = json['data']

        self._caps = result['cap']
        self._csrftoken = result['CSRFPreventionToken']
        await self.update_ticket(result['ticket'])

    async def _make_connection(self):
        headers = {}
        cookies = {}
        if self._ticket is not None:
            cookies['PVEAuthCookie'] = urllib.parse.quote_plus(self._ticket)
        if self._csrftoken is not None:
            headers['CSRFPreventionToken'] = self._csrftoken

        try:
            self._session = await aiohttp.ClientSession(
                headers=headers,
                cookies=cookies,
                conn_timeout=self.timeout,
            ).__aenter__()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            raise ConnectionException(e)

        # User supplied a fingerprint use that.
        if self.fingerprint is not None:
            return

        # Get the fingerprint from the remote and verify that.
        bad_fp = b'0'*32
        exc = None
        try:
            await self._session.get(self._url, ssl=aiohttp.Fingerprint(bad_fp))
        except aiohttp.ServerFingerprintMismatch as e:
            exc = e
        except aiohttp.client_exceptions.ClientConnectorError as e:
            raise ConnectionException(e)

        if exc is not None:
            hex_fp = _binary_fp_to_hex(exc.got)
            if not self._verify_cb(self._host, exc.got, hex_fp):
                # Close the session
                await self._close_connection()

                raise VerifyException("Failed to verify: %s" % hex_fp)

            self._fingerprint = exc.got

    async def _close_connection(self):
        await self._session.__aexit__(None, None, None)
        self._session = None

    async def __aenter__(self):
        await self._make_connection()
        return self

    async def __aexit__(self, *args):
        await self._close_connection()
