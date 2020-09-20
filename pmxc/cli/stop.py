import logging

from pmxc.api2client.exception import HTTPException
from pmxc.lib.utils import get_vmid_resource
from pmxc.lib.remote import RemoteConnection


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Stop (kill) a Virtual Machine/Container"


def configure_argparse(subparser):
    subparser.add_argument("remote_vmid", help="The remote:vmid")


async def execute(loop, config, args):
    try:
        async with RemoteConnection(loop, config, args['remote_vmid']) as conn:
            resource = await get_vmid_resource(conn, args['remote_vmid'])
            if not resource:
                return 1

            await resource.status.stop.post()
            print("OK")

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
