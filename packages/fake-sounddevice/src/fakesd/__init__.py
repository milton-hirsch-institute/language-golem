# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from fakesd import devices
from fakesd import patching

DeviceManager = devices.DeviceManager
Device = devices.Device
FakeInputStream = devices.FakeInputStream
FakeRawInputStream = devices.FakeRawInputStream
HostApi = devices.HostApi

setup = patching.setup

__all__ = [
    "DeviceManager",
    "Device",
    "FakeInputStream",
    "FakeRawInputStream",
    "HostApi",
    "setup",
]
