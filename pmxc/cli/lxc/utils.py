import logging

from pmxc.lib.utils import REMOTE_VMID_RE


__all__ = [
    "get_lxc_resource"
]


async def get_lxc_resource(conn, remote_vmid):
    match = REMOTE_VMID_RE.match(remote_vmid)
    if match is None:
        logging.error('Not a remote:vmid: %s', remote_vmid)
        return False

    vmid = int(match.group('vmid'))

    resources = await conn.cluster.resources.get()

    lxc = [x for x in resources if x['type'] == 'lxc' and x['vmid'] == vmid]
    if len(lxc) < 1:
        logging.error('VMID %d not found', vmid)
        return False
    if len(lxc) > 1:
        logging.error('More than one LXC with that vmid found: %d', vmid)
        return False

    node = lxc[0]['node']

    return conn.nodes(node).lxc(vmid)
