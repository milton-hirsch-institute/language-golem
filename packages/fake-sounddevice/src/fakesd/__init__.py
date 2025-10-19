# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from fakesd import devices
from fakesd import patching
from fakesd import streaming

AudioCallback = streaming.AudioCallback
Device = devices.Device
DeviceManager = devices.DeviceManager
FakeRawInputStream = streaming.FakeRawInputStream
FakeStream = streaming.FakeStream
HostApi = devices.HostApi

setup = patching.setup

__all__ = [
    "AudioCallback",
    "Device",
    "DeviceManager",
    "FakeRawInputStream",
    "FakeStream",
    "HostApi",
    "setup",
]
