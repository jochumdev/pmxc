import os.path
import sys

from pmxc import __version__


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Print Version and exit"


def configure_argparse(_):
    pass


async def execute(*_):
    print("%s version %s" % (os.path.basename(sys.argv[0]), __version__))
    return 0
