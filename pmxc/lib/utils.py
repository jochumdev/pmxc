import logging
import os
import platform
import re
import shutil


__all__ = [
    'REMOTE_RE',
    'REMOTE_VMID_RE',
    'SPICE_VIEWER_PATHS',
    'parse_key_value_string',
    'get_vmid_resource',
]

REMOTE_RE = re.compile(r'^(?P<remote>[\w\d\.\-\_]+):?')
REMOTE_VMID_RE = re.compile(r'^(?P<remote>[\w\d\.\-\_]+):(?P<vmid>[\d]+)$')


SPICE_VIEWER_PATHS = {
    'Linux': ['remote-viewer'],
    'Windows': ['VirtViewer v6.0-256\\bin\\remote-viewer'],
}

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

def find_path(paths):
    os_name = platform.system()

    if os_name.startswith('CYGWIN_NT'):
        os_name = 'Windows'

    executables = paths[os_name]

    if os_name == 'Linux' or os_name == 'Darwin':
        for executable in executables:
            cmd = shutil.which(executable)
            if cmd is not None:
                return cmd
    elif os_name == 'Windows':
        x32 = os.environ['ProgramFiles(x86)']
        x64 = os.environ['ProgramW6432']

        for executable in executables:
            cmd = os.path.join(x64, executable)
            if os.access(cmd, mode=os.F_OK | os.X_OK):
                return cmd
            cmd = os.path.join(x32, executable)
            if os.access(cmd, mode=os.F_OK | os.X_OK):
                return cmd

    return None
