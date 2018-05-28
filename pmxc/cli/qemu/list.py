import json
import logging

import texttable

from pmxc.api2client.exception import HTTPException
from pmxc.lib.remote import RemoteConnection
from pmxc.lib.utils import parse_key_value_string


__all__ = [
    "DESCRIPTION",
    "configure_argparse",
    "execute",
]

DESCRIPTION = "List QEMU Virtual Machines"


def configure_argparse(subparser):
    subparser.add_argument('-f', '--format',
                           help='output format [table|json] (default "table")',
                           dest='format',
                           default='table',
                           required=False)

    subparser.add_argument('-c', '--columns',
                           help='Columns (default "nvhsc")',
                           dest='columns',
                           default='nvhsc',
                           required=False)

    subparser.add_argument("remote", help="The remote")


async def execute(loop, config, args):
    qemus = []
    try:
        async with RemoteConnection(loop, config, args['remote']) as conn:
            resources = await conn.cluster.resources.get()

            for qemu in filter(lambda x: x['type'] == 'qemu', resources):
                node = qemu['node']
                vmid = qemu['vmid']

                try:
                    qemu_cfg = await conn.nodes(node).qemu(vmid).config.get()
                    qemu_cfg['node'] = node
                    qemu_cfg['vmid'] = vmid
                    qemu_cfg['status'] = qemu['status']

                    for i in range(0, 9):
                        key = "net" + str(i)
                        if key in qemu_cfg:
                            qemu_cfg[key] = parse_key_value_string(qemu_cfg[key])

                    # qemu_cfg['rootfs'] = parse_key_value_string(qemu_cfg['rootfs'])

                    qemus.append(qemu_cfg)
                except HTTPException as e:
                    logging.error("HTTP Error: %s", e)

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1

    if args['format'] == 'json':
        print(json.dumps(qemus, sort_keys=True, indent=4))
    else:
        _print_table(qemus, args)

    return 0

def _print_table(qemus, args):
    columns = list(args['columns'].replace(',', ''))

    available_headers = {
        'n': ('Node', 10,),
        'v': ('VMID', 5,),
        'h': ('Name', 20,),
        's': ('Status', 10,),
        'c': ('CPU', 6,),
    }

    headers = []
    sizes = []
    for c in columns:
        headers.append(available_headers[c][0])
        sizes.append(available_headers[c][1])

    table = texttable.Texttable()
    table.header(headers)
    table.set_cols_width(sizes)

    for qemu in qemus:
        row = []

        available_data = {
            'n': qemu['node'],
            'v': qemu['vmid'],
            'h': qemu['name'],
            's': qemu['status'],
            'c': qemu['cpu'] if 'cpu' in qemu else '',
        }

        for c in columns:
            row.append(available_data[c])

        table.add_row(row)

    print(table.draw())