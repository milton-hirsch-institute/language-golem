# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

"""Setup and configuration utilities for fake sounddevice testing."""

import contextlib
from collections.abc import Iterator

import sounddevice as sd

from fakesd import devices
from fakesd import monkeypatch
from fakesd import streaming


@contextlib.contextmanager
def setup(
    device_manager: devices.DeviceManager | None = None,
) -> Iterator[devices.DeviceManager]:
    """Set up fake sounddevice environment for testing.

    Args:
        device_manager: Optional DeviceManager instance. If None, creates a basic one.

    Yields:
        DeviceManager instance configured for the test session.
    """
    if device_manager is None:
        device_manager = devices.DeviceManager.new_basic()
    with monkeypatch.Patcher() as patcher:
        patcher.patch(sd, "query_devices", device_manager.query_devices)
        patcher.patch(sd, "RawInputStream", streaming.FakeRawInputStream)
        yield device_manager
