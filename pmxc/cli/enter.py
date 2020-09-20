import sys
import logging

import click
import aiohttp
from yarl import URL

from pmxc.api2client.exception import HTTPException
from pmxc.api2client.wsterminal import WSTerminal
from pmxc.lib.utils import get_vmid_resource
from pmxc.lib.remote import RemoteConnection
from pmxc.lib.utils import coro


__all__ = [
    "command",
]

@click.command(name='enter', help="Enter a VM/Container")
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

            termproxy = await resource.termproxy.post()
            path_vncwebsocket = resource.vncwebsocket.path

            websocket_url = URL(conn.url).with_path(path_vncwebsocket).with_query({
                "port": termproxy['port'],
                "vncticket": termproxy['ticket'],
            })

            if sys.stdin.isatty():
                print('Connecting: %s' % path_vncwebsocket)

            async with conn.session.ws_connect(str(websocket_url), ssl=aiohttp.Fingerprint(conn.binary_fingerprint), protocols=('binary',)) as ws:
                await WSTerminal(loop, ws, termproxy['user'], termproxy['ticket']).run()

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
