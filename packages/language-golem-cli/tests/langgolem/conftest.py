# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterator

import fakesd
import pytest


@pytest.fixture
def fake_sd() -> Iterator[fakesd.DeviceManager]:
    with fakesd.setup() as device_manager:
        yield device_manager
