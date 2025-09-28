# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from fakesd import devices
from fakesd import patching
from fakesd import streaming

AudioInputCallback = streaming.AudioInputCallback
Device = devices.Device
DeviceManager = devices.DeviceManager
FakeInputStream = streaming.FakeInputStream
FakeRawInputStream = streaming.FakeRawInputStream
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
