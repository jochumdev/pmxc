import argparse
import logging
import sys
import click

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


@click.group()
@click.option('--config', help="Application configuration file", default=DEFAULT_CONFIG_FILE)
@click.option('--debug', 'verbosity', flag_value=logging.DEBUG, default=False)
@click.option('--quiet', 'verbosity', flag_value=logging.CRITICAL, default=False)
@click.pass_context
def cli(ctx, config, verbosity):
    """proxmox Command-Line Interface"""

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    level = verbosity or DEFAULT_LOG_LEVEL
    logging.basicConfig(level=level, format=DEFAULT_LOG_FORMAT)

    if UVLOOP_AVAILABLE:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    ctx.obj['config'] = load_config(config)
    ctx.obj['loop'] = asyncio.get_event_loop()


# Load all commands (importlib.import_module) and add them as command to cli
cmds = load_all(pmxc.cli)
for _, cmd in cmds.items():
    if hasattr(cmd, 'command'):
        cli.add_command(cmd.command)
    if hasattr(cmd, 'group'):
        cli.add_command(cmd.group)