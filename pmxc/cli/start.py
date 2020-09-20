import click
import logging

from pmxc.api2client.exception import HTTPException
from pmxc.lib.utils import get_vmid_resource
from pmxc.lib.remote import RemoteConnection
from pmxc.lib.utils import coro


__all__ = [
    "command",
]

@click.command(name='start', help="Start a Virtual Machine/Container")
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

            await resource.status.start.post()
            print("OK")

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
