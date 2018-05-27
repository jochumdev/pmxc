import json
import texttable
from copy import deepcopy

__all__ = [
    'DESCRIPTION',
    'configure_argparse',
    'execute',
]

DESCRIPTION = 'List remotes'

def configure_argparse(subparser):
    subparser.add_argument('-f', '--format',
                           help='output format [table|json] (default "table")',
                           dest='format',
                           default='table',
                           required=False)

async def execute(loop, config, args):
    if 'remotes' not in config:
        return 1

    if args['format'] == 'json':

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