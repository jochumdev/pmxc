import logging

from pmxc.api2client.exception import HTTPException
from pmxc.cli.lxc.utils import get_lxc_resource
from pmxc.lib.remote import RemoteConnection


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "Resume a LinuX Container"


def configure_argparse(subparser):
    subparser.add_argument("remote_vmid", help="The remote:vmid")


async def execute(loop, config, args):
    try:
        async with RemoteConnection(loop, config, args['remote_vmid']) as conn:
            lxc_resource = await get_lxc_resource(conn, args['remote_vmid'])
            if not lxc_resource:
                return 1

            await lxc_resource.status.resume.post()
            print("OK")

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1
