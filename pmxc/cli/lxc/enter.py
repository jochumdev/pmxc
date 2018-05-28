import logging

import aiohttp
from yarl import URL

from pmxc.api2client.exception import HTTPException
from pmxc.api2client.wsterminal import WSTerminal
from pmxc.lib.utils import get_vmid_resource
from pmxc.lib.remote import RemoteConnection


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Enter a LinuX Container"


def configure_argparse(subparser):
    subparser.add_argument("remote_vmid", help="The remote:vmid")


async def execute(loop, config, args):
    try:
        async with RemoteConnection(loop, config, args['remote_vmid']) as conn:
            resource = await get_vmid_resource('lxc', conn, args['remote_vmid'])
            if not resource:
                return 1

            termproxy = await resource.termproxy.post()
            path_vncwebsocket = resource.vncwebsocket.path

            websocket_url = URL(conn.url).with_path(path_vncwebsocket).with_query({
                "port": termproxy['port'],
                "vncticket": termproxy['ticket'],
            })

            print('Connecting: %s' % path_vncwebsocket)
            async with conn.session.ws_connect(str(websocket_url), ssl=aiohttp.Fingerprint(conn.binary_fingerprint), protocols=('binary',)) as ws:
                await WSTerminal(loop, ws, termproxy['user'], termproxy['ticket']).run()

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
