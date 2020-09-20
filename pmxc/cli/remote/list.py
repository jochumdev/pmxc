import click
import json
import texttable
from copy import deepcopy

from pmxc.lib.utils import coro

__all__ = [
    'command',
]

@click.command(name='list', help="List remotes")
@click.option('-f', '--format', '_format', help='output format [table|json] (default "table")', default='table')
@coro
@click.pass_context
async def command(ctx, _format):
    config = ctx.obj['config']

    if 'remotes' not in config:
        return 1

    if _format == 'json':

        remotes = deepcopy(config['remotes'])
        for key in remotes.keys():
            if 'password' in remotes[key]:
                del(remotes[key]['password'])

        print(json.dumps(remotes, sort_keys=True, indent=4))
    else:
        table = texttable.Texttable()
        table.header([ 'Name', 'Host', 'Port', 'Username', 'Fingerprint', ])
        table.set_cols_width((10, 25, 6, 15, 95))

        for name, data in config['remotes'].items():
            table.add_row((name, data['host'], data['port'], data['username'], data['fingerprint'],))
        print(table.draw())

    return 0