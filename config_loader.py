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
from typing import Dict, Tuple

import yaml


def load_config(filename: str) -> Dict:
    with open(filename) as f:
        return yaml.safe_load(f)


def load_configs(infra_file, test_file) -> Tuple[Dict, Dict]:
    return load_config(infra_file), load_config(test_file)
