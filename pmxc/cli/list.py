import json
import logging

import click
import texttable

from pmxc.api2client.exception import HTTPException
from pmxc.lib.remote import RemoteConnection
from pmxc.lib.utils import parse_key_value_string
from pmxc.lib.utils import coro


__all__ = [
    "command",
]

@click.command(name='list', help="List Virtual Machines/Containers")
@click.option('-f', '--format', 'format', help='output format [table|json] (default "table")', default='table')
@click.option('-c', '--columns', 'columns', help='Columns (default "ntvhsarm46")', default='ntvhsarm46')
@click.argument('remote')
@coro
@click.pass_context
async def command(ctx, format, columns, remote):

    resources = []
    try:
        async with RemoteConnection(ctx.obj['loop'], ctx.obj['config'], remote) as conn:
            cresources = await conn.cluster.resources.get()

            for resource in filter(lambda x: (x['type'] == 'resource' or x['type'] == 'qemu' or x['type'] == 'lxc'), cresources):
                if resource['type'] == 'lxc':
                    node = resource['node']
                    vmid = resource['vmid']

                    try:
                        lxc_cfg = await conn.nodes(node).lxc(vmid).config.get()
                        lxc_cfg['type'] = resource['type']
                        lxc_cfg['node'] = node
                        lxc_cfg['vmid'] = vmid
                        lxc_cfg['status'] = resource['status']

                        for i in range(0, 9):
                            key = "net" + str(i)
                            if key in lxc_cfg:
                                lxc_cfg[key] = parse_key_value_string(lxc_cfg[key])

                        lxc_cfg['rootfs'] = parse_key_value_string(lxc_cfg['rootfs'])

                        resources.append(lxc_cfg)
                    except HTTPException as e:
                        logging.error("HTTP Error: %s", e)
                else:
                    node = resource['node']
                    vmid = resource['vmid']
                    rtype = resource['type']

                    try:
                        resource_cfg = await conn.nodes(node).url_join(rtype, str(vmid)).config.get()
                        resource_cfg['type'] = rtype
                        resource_cfg['node'] = node
                        resource_cfg['vmid'] = vmid
                        resource_cfg['status'] = resource['status']

                        for i in range(0, 9):
                            key = "net" + str(i)
                            if key in resource_cfg:
                                resource_cfg[key] = parse_key_value_string(resource_cfg[key])

                        if (rtype == 'resource'):
                            resource_cfg['rootfs'] = parse_key_value_string(resource_cfg['rootfs'])
                        else:
                            resource_cfg['arch'] = 'unknown'
                            resource_cfg['hostname'] = ''
                            resource_cfg['rootfs'] = {'size': 0}

                        resources.append(resource_cfg)
                    except HTTPException as e:
                        logging.error("HTTP Error: %s", e)

    except HTTPException as e:
        logging.fatal("HTTP Error: %s", e)
        return 1

    if format == 'json':
        print(json.dumps(resources, sort_keys=True, indent=4))
    else:
        _print_table(resources, columns)

    return 0

def _print_table(resources, columns):
    columns = list(columns.replace(',', ''))

    available_headers = {
        'n': ('Node', 10,),
        't': ('Type', 5,),
        'v': ('VMID', 5,),
        'h': ('Hostname', 20,),
        'a': ('Arch/CPU', 10,),
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

    for resource in resources:
        if resource['type'] == 'qemu':
            row = []

            net4 = ''
            net6 = ''

            for i in range(0, 9):
                key = "net" + str(i)
                if key in resource:
                    if 'ip' in resource[key]:
                        if net4 != '':
                            net4 += '\n'
                        net4 += resource[key]['ip'] + " (" + resource[key]['name'] + ")"
                    if 'ip6' in resource[key]:
                        if net6 != '':
                            net6 += '\n'
                        net6 += resource[key]['ip6'] + " (" + resource[key]['name'] + ")"

            arch = ''
            if resource['type'] == 'resource':
                arch = resource['arch']
            elif resource['type'] == 'qemu' and 'cpu' in resource:
                arch = resource['cpu']

            available_data = {
                'n': resource['node'],
                't': resource['type'],
                'v': resource['vmid'],
                'h': resource['hostname'] if resource['type'] == 'resource' else resource['name'],
                'a': arch,
                'r': resource['rootfs']['size'],
                'm': resource['memory'],
                's': resource['status'],
                '4': net4,
                '6': net6
            }

            for c in columns:
                row.append(available_data[c])

        elif resource['type'] == 'lxc':
            row = []

            net4 = ''
            net6 = ''

            for i in range(0, 9):
                key = "net" + str(i)
                if key in resource:
                    if 'ip' in resource[key]:
                        if net4 != '':
                            net4 += '\n'
                        net4 += resource[key]['ip'] + " (" + resource[key]['name'] + ")"
                    if 'ip6' in resource[key]:
                        if net6 != '':
                            net6 += '\n'
                        net6 += resource[key]['ip6'] + " (" + resource[key]['name'] + ")"

            available_data = {
                'n': resource['node'],
                't': resource['type'],
                'v': resource['vmid'],
                'h': resource['hostname'],
                'a': resource['arch'],
                'r': resource['rootfs']['size'],
                'm': resource['memory'],
                's': resource['status'],
                '4': net4,
                '6': net6
            }

            for c in columns:
                row.append(available_data[c])

        table.add_row(row)

    print(table.draw())