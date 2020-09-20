import os
import click
from pmxc.lib.loader import load_all

__all__ = [
    'group'
]

class objectview(object):
    """Convert dict(or parameters of dict) to object view
    See also:
        - https://goodcode.io/articles/python-dict-object/
        - https://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    >>> o = objectview({'a': 1, 'b': 2})
    >>> o.a, o.b
    (1, 2)
    >>> o = objectview(a=1, b=2)
    >>> o.a, o.b
    (1, 2)
    """
    def __init__(self, *args, **kwargs):
        d = dict(*args, **kwargs)
        self.__dict__ = d

@click.group(name='remote')
def group():
    pass

# Load all commands (importlib.import_module) and add them as command to cli
cmds = load_all(objectview(__path__ = [os.path.dirname(__file__),], __name__ = __name__))
for _, cmd in cmds.items():
    if hasattr(cmd, 'command'):
        group.add_command(cmd.command)
