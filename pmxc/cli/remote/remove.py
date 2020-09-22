import sys
import click
import logging
from pmxc.lib.utils import coro
from pmxc.lib.config import save_config

__all__ = [
    'command',
]

@click.command(name='remove', help="Remove a remote")
@click.argument('remote')
@coro
@click.pass_context
async def command(ctx, remote):
    config = ctx.obj['config']

    if 'remotes' not in config or remote not in config['remotes']:
        print('Unknown remote "%s"' % remote, file=sys.stderr)
        return 1

    del(config['remotes'][remote])

    save_config(config, ctx.obj['config_path'])

    print("OK")

    return 0