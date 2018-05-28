import logging
import re

__all__ = [
    'REMOTE_RE',
    'REMOTE_VMID_RE',
    'parse_key_value_string',
    'get_vmid_resource',
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

async def get_vmid_resource(rtype, conn, remote_vmid):
    match = REMOTE_VMID_RE.match(remote_vmid)
    if match is None:
        logging.error('Not a remote:vmid: %s', remote_vmid)
        return False

    vmid = int(match.group('vmid'))

    resources = await conn.cluster.resources.get()

    r = [x for x in resources if x['type'] == rtype and x['vmid'] == vmid]
    if len(r) < 1:
        logging.error('VMID %d not found', vmid)
        return False
    if len(r) > 1:
        logging.error('More than one %s with that vmid found: %d', rtype, vmid)
        return False

    node = r[0]['node']

    return conn.nodes(node).url_join(rtype, str(vmid))