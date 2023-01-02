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
from mfd_network_adapter import NetworkPort
from mfd_network_adapter.network_port.exceptions import IPAddressesNotFound


def set_ip(port: NetworkPort, ip):
    """
    Set IP if required.
    :param port:
    :param ip:
    :return:
    """
    try:
        port.interface_name=port.get_interface_name().split("\n")[0]
        ips = port.get_ips()
    except IPAddressesNotFound:
        ips = []
    if ip not in ips:
        output=port.add_ip(ip)          


def cleanup_ip(port: NetworkPort, ip):
    """
    Remove IP if required.
    :param port:
    :param ip:
    :return:
    """
    try:
        ips = port.get_ips()
    except IPAddressesNotFound:
        ips = []
    if ip in ips:
        port.del_ip(ip)
