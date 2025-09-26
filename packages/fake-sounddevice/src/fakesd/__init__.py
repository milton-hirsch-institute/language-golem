# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from fakesd import devices
from fakesd import patching

AudioInputCallback = devices.AudioInputCallback
Device = devices.Device
DeviceManager = devices.DeviceManager
FakeInputStream = devices.FakeInputStream
FakeRawInputStream = devices.FakeRawInputStream
HostApi = devices.HostApi

setup = patching.setup

__all__ = [
    "AudioInputCallback",
    "Device",
    "DeviceManager",
    "FakeInputStream",
    "FakeRawInputStream",
    "HostApi",
    "setup",
]
