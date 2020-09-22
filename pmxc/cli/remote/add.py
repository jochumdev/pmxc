import sys
import click
import getpass
import logging
import re

from pmxc.api2client.connection import Connection
from pmxc.api2client.exception import AuthenticationException
from pmxc.api2client.exception import VerifyException
from pmxc.lib.utils import REMOTE_RE
from pmxc.cli.remote import group
from pmxc.lib.utils import coro
from pmxc.lib.config import save_config


__all__ = [
    "command",
]


# def configure_argparse(subparser):
#     subparser.add_argument("name", help="The name of the remote")
#     subparser.add_argument(
#         "host", help="The host, either host, host:port or https://host:port")
#     subparser.add_argument("username", help="The username")


@click.command(name='add', help="Add a remote")
@click.argument('name')
@click.argument('host')
@click.argument('username')
@coro
@click.pass_context
async def command(ctx, name, host, username):
    loop = ctx.obj['loop']
    config = ctx.obj['config']

    match = REMOTE_RE.match(name)
    if match is None:
        print('"%s" is a invalid remote name' % name, file=sys.stderr)
        return 1

    name = match.group('remote')

    if 'remotes' in config and name in config['remotes']:
        print('The remote "%s" has already been registered' % name, file=sys.stderr)
        return 1

    match = re.fullmatch(
        r"(?P<scheme>[a-z][a-z0-9+\-.]*:\/\/)?"
        r"(?P<host>[a-z0-9\-._~%]+|\[[a-z0-9\-._~%!\$&'()*+,;=:]+\])"
        r":?(?P<port>[0-9]+)?", host
    )
    if match is None:
        print('The given host "%s" is not valid' % host, file=sys.stderr)
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
                await conn.login(username, password)

    except VerifyException:
        print('Aborting, you didn\'t verify the fingerprint', file=sys.stderr)
        return 1

    except AuthenticationException:
        print("Aborting, authentication failed", file=sys.stderr)
        return 1

    if 'remotes' not in config:
        config['remotes'] = {}

    config['remotes'][name] = {
        'host': host,
        'port': port,
        'username': username,
        'fingerprint': fingerprint,
    }
    if password != '':
        config['remotes'][name]['password'] = password

    save_config(config, ctx.obj['config_path'])

    return 0
