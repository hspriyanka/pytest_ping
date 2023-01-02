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
import time

import pytest
from mfd_ping import Ping
from netaddr import IPNetwork

from libs.network_utilities.adapters import network_port
from libs.network_utilities.ips import set_ip, cleanup_ip


class TestPing:
    @pytest.fixture(scope="session")
    def sut_network_port(self, sut_machine):
        return network_port(sut_machine)

    @pytest.fixture(scope="session")
    def client_network_port(self, client_machine):
        return network_port(client_machine)

    @pytest.fixture(scope="session")
    def tested_ips(self, sut_network_port, client_network_port):
        # prepare
        dst_ip = IPNetwork("198.108.8.1/24")
        src_ip = IPNetwork("198.108.8.3/24")
        set_ip(sut_network_port, src_ip)
        set_ip(client_network_port, dst_ip)
        yield src_ip, dst_ip
        # teardown
        cleanup_ip(sut_network_port, src_ip)
        cleanup_ip(client_network_port, dst_ip)

    def test_ping_params_from_config(self, sut_machine, client_machine, tested_ips, mtu, count, packet_size, timeout):
        ping = Ping(connection=sut_machine["established_connection"])
        src_ip, dst_ip = tested_ips
        print("\n--------------------Ping from SUT to Client---------------------------")
        results = self.make_ping(count, dst_ip, mtu, packet_size, ping, src_ip, timeout)
        print("packets_transmitted:",results.packets_transmitted,"\nPackets_received:",results.packets_received)
        ping = Ping(connection=client_machine["established_connection"])
        print("\n--------------------Ping from Client to SUT-----------------------------")
        results1 = self.make_ping(count, src_ip, mtu, packet_size, ping, dst_ip, timeout)
        print("packets_transmitted:",results1.packets_transmitted,"\nPackets_received:",results1.packets_received)
        print("***************************************************************************")
        assert results.fail_count == 0 and results1.fail_count == 0
        assert results.pass_count == 10 and results1.pass_count == 10
        #assert results.fail_count == 0
        #assert results.pass_count == 10

    def make_ping(self, count, dst_ip, mtu, packet_size, ping, src_ip, timeout):
        ping_process = ping.start(dst_ip=dst_ip.ip, src_ip=src_ip.ip, mtu=mtu, count=count, packet_size=packet_size,
                                  timeout=timeout)
        time.sleep(timeout)
        results = ping.stop(ping_process)
        return results
