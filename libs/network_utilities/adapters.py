# INTEL CONFIDENTIAL
# Copyright 2022-2022 Intel Corporation.
#
# This software and the related documents are Intel copyrighted materials, and your use of them is governed
# by the express license under which they were provided to you ("License"). Unless the License provides otherwise,
# you may not use, modify, copy, publish, distribute, disclose or transmit this software or the related documents
# without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or implied warranties,
# other than those that are expressly stated in the License.

from mfd_network_adapter.network_adapters_owner.linux import LinuxNetworkAdaptersOwner
from mfd_typing import VendorID, DeviceID, SubDeviceID, SubVendorID, PCIDevice
from netaddr import IPAddress, AddrFormatError


def resolve_adapter_id(adapter_id):
    """Resolve adapter identifier to (ports, filters) tuple.

    :param adapter_id - adapter identifier in AGAT, supported format:
        vid:did; example input: '8086:0abc'
        vid:did:subd; example input: '8086:0abc:0000'
        vid:did, ports; example input: '8086:0abc,1,2'
        vid:did:subd, ports; example input: '8086:0abc:0000,1,2'
        name; example input: 'Intel(R) Ethernet Network Adapter XXXX NVMe'
        eth; example input: 'vmnic1'
        pci; example input: '00:04:00.0'
        mac_address; example input: '3c:fd:fe:4e:26:a8'
    :type adapter_id - str
    :return tuple(ports, filters)
    """
    filters = {}
    ports = ["1"]

    # MAC address, example input: '3c:fd:fe:4e:26:a8'
    if adapter_id.count(":") == 5:
        filters["mac_address"] = adapter_id

    # PCI, example input: '00:04:00.0'
    elif adapter_id.find(":") == 2 and "." in adapter_id:
        filters["pci"] = adapter_id

    # Example input vid:did ('8086:0abc') or vid:did, ports ('8086:0abc,1')
    elif adapter_id.count(":") == 1:
        split_adapter_id = adapter_id.split(",")
        vid, did = split_adapter_id[0].split(":")
        filters["vendor_id"] = VendorID(vid)
        filters["device_id"] = DeviceID(did)
        filters["sub_device_id"] = SubDeviceID(0)
        filters["sub_vendor_id"] = SubVendorID(0)

        if split_adapter_id[1:]:
            ports = split_adapter_id[1:]

    # Example input vid:did:subd ('8086:0abc:0000')
    # or vid:did:subd, ports ('8086:0abc:0000,1')
    elif adapter_id.count(":") == 2:
        split_adapter_id = adapter_id.split(",")
        vid, did, subd = split_adapter_id[0].split(":")
        filters["vendor_id"] = VendorID(vid)
        filters["device_id"] = DeviceID(did)
        filters["sub_device_id"] = SubDeviceID(subd)
        filters["sub_vendor_id"] = SubVendorID(0)

        if split_adapter_id[1:]:
            ports = split_adapter_id[1:]

    else:
        filters["eth"] = adapter_id

    return ports, filters


def network_port(machine):
    connection = machine["established_connection"]
    owner = LinuxNetworkAdaptersOwner(connection=connection)
    port_id = machine["tested_adapter_id"]
    port_nr, filters = resolve_adapter_id(port_id)
    port_nr = int(port_nr[0])
    if "eth" in filters:
        port = [port for port in owner.get_ports() if
                port.interface_name == filters["eth"]][0]
    elif "vendor_id" in filters:
        adapter = owner.get_adapter(PCIDevice(**filters))
        ports = owner.get_ports(adapter)
        if len(ports) >= port_nr:
            port = ports[port_nr - 1]
    else:
        raise Exception("")
    return port
