import click
import logging
import os
import subprocess
from tempfile import mkstemp

from pmxc.api2client.exception import HTTPException
from pmxc.lib.remote import RemoteConnection
from pmxc.lib.utils import SPICE_VIEWER_PATHS
from pmxc.lib.utils import find_path
from pmxc.lib.utils import get_vmid_resource
from pmxc.lib.utils import is_cygwin
from pmxc.lib.utils import randstring
from pmxc.lib.utils import coro

__all__ = [
    "command",
]

@click.command(name='spice', help="Connect with spice to the Virtual Machine/Container")
@click.argument('remote')
@click.argument('vmid', default="")
@coro
@click.pass_context
async def command(ctx, remote, vmid):
    loop = ctx.obj['loop']
    config = ctx.obj['config']
    try:
        async with RemoteConnection(loop, config, remote) as conn:
            resource = await get_vmid_resource(conn, remote, vmid)
            if not resource:
                return 1

            spdata = await resource.spiceproxy.post()

            filecontents = "[virt-viewer]\n"
            for k, v in spdata.items():
                filecontents += str(k) + "=" + str(v) + "\n"

            filename = None
            if not is_cygwin():
                fd, filename = mkstemp(text=True)

                with open(filename, 'w') as fp:
                    fp.write(filecontents)
                os.close(fd)
            else:
                filename = os.path.join(os.getenv('USERPROFILE'), randstring() + ".vv")
                with open(filename, 'w') as fp:
                    fp.write(filecontents)

            executable = find_path(SPICE_VIEWER_PATHS)
            subprocess.Popen([executable, filename], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
