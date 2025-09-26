# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterator

import fakesd
import pytest
from click import testing


@pytest.fixture
def runner() -> testing.CliRunner:
    return testing.CliRunner()


@pytest.fixture
def fake_sd() -> Iterator[fakesd.DeviceManager]:
    with fakesd.setup() as device_manager:
        yield device_manager
