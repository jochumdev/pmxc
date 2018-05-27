import getpass

from pmxc.api2client.connection import Connection
from pmxc.lib.utils import REMOTE_RE


__all__ = [
    'RemoteConnection',
]

class RemoteConnection(object):
    def __init__(self, loop, config, name, verify_cb=None):
        match = REMOTE_RE.match(name)
        if match is None:
            raise ValueError('"%s" is a invalid remote name' % name)

        name = match.group('remote')
        if name not in config['remotes']:
            raise ValueError('Unknown remote "%s"' % name)

        self._loop = loop
        self._config = config
        self._name = name
        self._verify_cb = verify_cb

        self._conn = None

    async def __aenter__(self):
        cfg = self._config['remotes'][self._name]
        self._conn = Connection(
            self._loop, cfg['host'], port=cfg['port'], fingerprint=cfg['fingerprint'], verify_cb=self._verify_cb)
        await self._conn.__aenter__()

        password = None
        if 'password' in cfg:
            password = cfg['password']
        else:
            password = getpass.getpass(
                'Enter the password for "%s": ' % self._name)

        await self._conn.login(cfg['username'], password)

        return self._conn

    async def __aexit__(self, *args):
        await self._conn.__aexit__(*args)
