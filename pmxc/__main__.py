import argparse
import logging
import sys

from pmxc import DEFAULT_CONFIG_FILE
from pmxc.lib.loader import load_all
from pmxc.lib.config import load_config
from pmxc.lib.config import save_config
import pmxc.cli

import asyncio
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(levelname)-8.8s  %(message)s'


async def run(cmd, loop, config, args):
    result = await cmd.execute(loop, config, args)
    if result != 0:
        sys.exit(result)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="proxmox Command-Line Interface",
    )

    subparsers = parser.add_subparsers(title="subcommands",
                                       description="Main pmx CLI commands",  # noqa
                                       dest="subcommand",
                                       help="Choose and run with --help")
    subparsers.required = True

    cmds = load_all(pmxc.cli)

    for name in sorted(cmds.keys()):
        if not hasattr(cmds[name], 'DESCRIPTION'):
            # Not a cmd, maybe a helper?
            continue

        subparser = subparsers.add_parser(name, help=cmds[name].DESCRIPTION)

        subparser.add_argument("--config",
                               help="Application configuration file",
                               dest="yaml_file",
                               required=False,
                               default=DEFAULT_CONFIG_FILE)

        subparser.add_argument("-q", "--quiet", action="store_const",
                               const=logging.CRITICAL, dest="verbosity",
                               help="Show only critical errors.")

        subparser.add_argument("-d", "--debug", action="store_const",
                               const=logging.DEBUG, dest="verbosity",
                               help="Show all messages, including debug messages.")  # noqa

        cmds[name].configure_argparse(subparser)

    # Parse command-line arguments
    parsed_args = vars(parser.parse_args(args))

    # Initialize logging
    level = parsed_args.get('verbosity') or DEFAULT_LOG_LEVEL
    logging.basicConfig(level=level, format=DEFAULT_LOG_FORMAT)

    config = load_config(parsed_args['yaml_file'])

    # Execute the command
    which_command = parsed_args['subcommand']

    if UVLOOP_AVAILABLE:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(cmds[which_command], loop, config, parsed_args))
    finally:
        loop.close()
        save_config(config, parsed_args['yaml_file'])
