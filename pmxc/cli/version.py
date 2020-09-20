import os
import sys
import click

from pmxc import __version__
from pmxc.lib.utils import coro

__all__ = [
    "command",
]

@click.command(name='version', help="Show the version")
@coro
@click.pass_context
async def command(ctx):
    print("%s version %s" % (os.path.basename(sys.argv[0]), __version__))
    return 0
