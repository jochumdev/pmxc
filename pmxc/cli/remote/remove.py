import logging

__all__ = [
    'DESCRIPTION',
    'configure_argparse',
    'execute',
]

DESCRIPTION = 'Remove a remote'

def configure_argparse(subparser):
    subparser.add_argument("name", help="The name of the remote")

async def execute(loop, config, args):
    if 'remotes' not in config or args['name'] not in config['remotes']:
        logging.fatal('Unknown remote "%s"' % args['name'])
        return 1

    del(config['remotes'][args['name']])

    print("OK")

    return 0