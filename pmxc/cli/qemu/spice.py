import os
import logging
from tempfile import mkstemp
import subprocess

from pmxc.api2client.exception import HTTPException
from pmxc.lib.utils import get_vmid_resource, SPICE_VIEWER_PATHS, find_path
from pmxc.lib.remote import RemoteConnection


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Connect with spice to the QEMU Virtual Machine"


def configure_argparse(subparser):
    subparser.add_argument("remote_vmid", help="The remote:vmid")


async def execute(loop, config, args):
    try:
        async with RemoteConnection(loop, config, args['remote_vmid']) as conn:
            resource = await get_vmid_resource('qemu', conn, args['remote_vmid'])
            if not resource:
                return 1

            spdata = await resource.spiceproxy.post()

            filecontents = "[virt-viewer]\n"
            for k, v in spdata.items():
                filecontents += str(k) + "=" + str(v) + "\n"

            fd, filename = mkstemp(text=True)
            with open(filename, 'w') as fp:
                fp.write(filecontents)
            os.close(fd)
            executable = find_path(SPICE_VIEWER_PATHS)
            subprocess.Popen([executable, filename], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1