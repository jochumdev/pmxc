import re

__all__ = [
    'REMOTE_RE',
    'REMOTE_VMID_RE',
    'parse_key_value_string'
]

REMOTE_RE = re.compile(r'^(?P<remote>[\w\d\.\-\_]+):?')
REMOTE_VMID_RE = re.compile(r'^(?P<remote>[\w\d\.\-\_]+):(?P<vmid>[\d]+)$')


def parse_key_value_string(data):
    split = data.split(',')

    result = {}
    for s in split:
        if '=' in s:
            key, value = s.split('=')
            result[key] = value
        else:
            result[''] = s

    return result