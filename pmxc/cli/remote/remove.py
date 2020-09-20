import click
import logging
from pmxc.lib.utils import coro

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
        logging.fatal('Unknown remote "%s"' % remote)
        return 1

    del(config['remotes'][remote])

    print("OK")

    return 0