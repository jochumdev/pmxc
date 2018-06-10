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

DESCRIPTION = "List LinuX Containers"


def configure_argparse(subparser):
    subparser.add_argument('-f', '--format',
                           help='output format [table|json] (default "table")',
                           dest='format',
                           default='table',
                           required=False)

    subparser.add_argument('-c', '--columns',
                           help='Columns (default "nvhsarm46")',
                           dest='columns',
                           default='nvhsarm46',
                           required=False)

    subparser.add_argument("remote", help="The remote")


async def execute(loop, config, args):
    lxcs = []
    try:
        async with RemoteConnection(loop, config, args['remote']) as conn:
            resources = await conn.cluster.resources.get()

            for lxc in filter(lambda x: x['type'] == 'lxc', resources):
                node = lxc['node']
                vmid = lxc['vmid']

                try:
                    lxc_cfg = await conn.nodes(node).lxc(vmid).config.get()
                    lxc_cfg['node'] = node
                    lxc_cfg['vmid'] = vmid
                    lxc_cfg['status'] = lxc['status']

                    for i in range(0, 9):
                        key = "net" + str(i)
                        if key in lxc_cfg:
                            lxc_cfg[key] = parse_key_value_string(lxc_cfg[key])

                    lxc_cfg['rootfs'] = parse_key_value_string(lxc_cfg['rootfs'])

                    lxcs.append(lxc_cfg)
                except HTTPException as e:
                    logging.error("HTTP Error: %s", e)

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1

    if args['format'] == 'json':
        print(json.dumps(lxcs, sort_keys=True, indent=4))
    else:
        _print_table(lxcs, args)

    return 0

def _print_table(lxcs, args):
    columns = list(args['columns'].replace(',', ''))

    available_headers = {
        'n': ('Node', 10,),
        'v': ('VMID', 5,),
        'h': ('Hostname', 20,),
        'a': ('Arch', 6,),
        'r': ('Rootfs (GiB)', 6,),
        'm': ('Memory (MiB)', 6,),
        's': ('Status', 10,),
        '4': ('IPv4', 24,),
        '6': ('IPv6', 35,),
    }

    headers = []
    sizes = []
    for c in columns:
        headers.append(available_headers[c][0])
        sizes.append(available_headers[c][1])

    table = texttable.Texttable()
    table.header(headers)
    table.set_cols_width(sizes)

    for lxc in lxcs:
        row = []

        net4 = ''
        net6 = ''

        for i in range(0, 9):
            key = "net" + str(i)
            if key in lxc:
                if 'ip' in lxc[key]:
                    if net4 != '':
                        net4 += '\n'
                    net4 += lxc[key]['ip'] + " (" + lxc[key]['name'] + ")"
                if 'ip6' in lxc[key]:
                    if net6 != '':
                        net6 += '\n'
                    net6 += lxc[key]['ip6'] + " (" + lxc[key]['name'] + ")"

        available_data = {
            'n': lxc['node'],
            'v': lxc['vmid'],
            'h': lxc['hostname'],
            'a': lxc['arch'],
            'r': lxc['rootfs']['size'],
            'm': lxc['memory'],
            's': lxc['status'],
            '4': net4,
            '6': net6
        }

        for c in columns:
            row.append(available_data[c])

        table.add_row(row)

    print(table.draw())