import sys
import logging

from pmxc import DEFAULT_CONFIG_FILE
from pmxc.lib.loader import load_all

__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "LinuX Container management"

_cmds = {}


def configure_argparse(subparser):
    global _cmds

    subparsers = subparser.add_subparsers(title="subcommands",
                                       description="LinuX Container CLI commands",  # noqa
                                       dest="subcommand_lxc",
                                       help="Choose and run with --help")
    subparsers.required = True

    _cmds = load_all(sys.modules[__name__])

    for name in sorted(_cmds.keys()):
        if not hasattr(_cmds[name], 'DESCRIPTION'):
            # Not a cmd, maybe a helper?
            continue

        subsubparser = subparsers.add_parser(name, help=_cmds[name].DESCRIPTION)

        subsubparser.add_argument("--config",
                                  help="Application configuration file",
                                  dest="yaml_file",
                                  required=False,
                                  default=DEFAULT_CONFIG_FILE)

        subsubparser.add_argument("-q", "--quiet", action="store_const",
                                  const=logging.CRITICAL, dest="verbosity",
                                  help="Show only critical errors.")

        subsubparser.add_argument("-d", "--debug", action="store_const",
                               const=logging.DEBUG, dest="verbosity",
                               help="Show all messages, including debug messages.")  # noqa

        _cmds[name].configure_argparse(subsubparser)


async def execute(loop, config, args):
    global _cmds

    which_command = args['subcommand_lxc']
    return await _cmds[which_command].execute(loop, config, args)
