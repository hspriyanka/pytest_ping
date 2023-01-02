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
import importlib
import logging

import pytest

from config_loader import load_config

# content of conftest.py

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption(
        "--infrastructure-file",
        action="store",
        required=True,
        help="Path/name of infrastructure file",
    )
    parser.addoption(
        "--test-config-file",
        action="store",
        required=True,
        help="Path/name of test config file",
    )


@pytest.fixture(scope="session")
def infrastructure_path(request):
    return request.config.getoption("--infrastructure-file")


@pytest.fixture(scope="session")
def infrastructure(infrastructure_path):
    return load_config(infrastructure_path)


@pytest.fixture(scope="session")
def test_config_path(request):
    return request.config.getoption("--test-config-file")


@pytest.fixture(scope="session")
def test_config(test_config_path):
    return load_config(test_config_path) if test_config_path else []


def machine_factory(label: str):
    def my_machine(infrastructure):
        for machine in infrastructure:
            if machine["label"] != label:
                continue
            conn_details = machine["connection"]
            connection_parameters = conn_details.get("connection_details")
            mfd_connect_class = getattr(importlib.import_module("mfd_connect"), conn_details['connection_type'])
            conn = mfd_connect_class(**connection_parameters)
            to_add = {"established_connection": conn, **machine}
            return to_add

    return my_machine


@pytest.fixture(scope="session")
def sut_machine(infrastructure):
    return machine_factory("sut")(infrastructure)


@pytest.fixture(scope="session")
def client_machine(infrastructure):
    return machine_factory("client")(infrastructure)


def read_test_config_file(metafunc):
    test_config = {}
    test_config_path = metafunc.config.getoption("--test-config-file")
    if test_config_path:
        test_config = load_config(test_config_path)
    return test_config


def parse_parameters_from_config_file(metafunc):
    test_config = read_test_config_file(metafunc)
    if not test_config:
        return
    test_parameters_from_file = test_config.keys()
    test_parameters_to_pass = [param for param in metafunc.fixturenames if param in test_parameters_from_file]
    argnames = ",".join(test_parameters_to_pass)
    argvalues = []
    for test_param in test_parameters_to_pass:
        argvalues.append(test_config.get(test_param))
    metafunc.parametrize(argnames, [tuple(argvalues)])


def pytest_generate_tests(metafunc):
    parse_parameters_from_config_file(metafunc)
