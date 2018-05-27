import getpass
import logging
import re

from pmxc.api2client.connection import Connection
from pmxc.api2client.exception import AuthenticationException
from pmxc.api2client.exception import VerifyException
from pmxc.lib.utils import REMOTE_RE


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Add a remote"


def configure_argparse(subparser):
    subparser.add_argument("name", help="The name of the remote")
    subparser.add_argument(
        "host", help="The host, either host, host:port or https://host:port")
    subparser.add_argument("username", help="The username")


async def execute(loop, config, args):
    match = REMOTE_RE.match(args['name'])
    if match is None:
        logging.fatal('"%s" is a invalid remote name', args['name'])
        return 1

    name = match.group('remote')

    if 'remotes' in config and name in config['remotes']:
        logging.fatal('The remote "%s" has already been registered',
                      name)
        return 1

    match = re.fullmatch(
        r"(?P<scheme>[a-z][a-z0-9+\-.]*:\/\/)?"
        r"(?P<host>[a-z0-9\-._~%]+|\[[a-z0-9\-._~%!\$&'()*+,;=:]+\])"
        r":?(?P<port>[0-9]+)?", args['host']
    )
    if match is None:
        logging.fatal('The given host "%s" is not valid', args['host'])
        return 1

    password = getpass.getpass(
        'Enter the password for "%s" (leave empty if you don\'t want to save it): ' % name)

    host = match.group('host')
    port = 8006
    if match.group('port') is not None:
        port = match.group('port')

    fingerprint = None
    try:
        async with Connection(loop, host, port=port) as conn:
            fingerprint = conn.fingerprint

            if password != '':
                await conn.login(args['username'], password)

    except VerifyException:
        logging.fatal('Aborting, you didn\'t verify the fingerprint')
        return 1

    except AuthenticationException:
        logging.fatal("Aborting, authentication failed")
        return 1

    if 'remotes' not in config:
        config['remotes'] = {}

    config['remotes'][name] = {
        'host': host,
        'port': port,
        'username': args['username'],
        'fingerprint': fingerprint,
    }
    if password != '':
        config['remotes'][args['name']]['password'] = password

    return 0
