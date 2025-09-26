# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterator

import fakesd
import pytest
import sounddevice
from click import testing
from langgolem.audio import devices


@pytest.fixture
def runner() -> testing.CliRunner:
    return testing.CliRunner()


@pytest.fixture
def fake_input_stream(monkeypatch) -> type[sounddevice.InputStream]:
    class FakeInputStream(sounddevice.InputStream):
        def __init__(
            self,
            samplerate: float,
            device: int,
            channels: int,
            dtype: str,
            callback: devices.AudioInputCallback,
        ):
            self._samplerate = samplerate
            self._device = device
            self._channels = channels
            self._dtype = dtype
            self._callback = callback

    monkeypatch.setattr(sounddevice, "InputStream", FakeInputStream)

    return FakeInputStream


@pytest.fixture
def fake_sd(fake_input_stream) -> Iterator[fakesd.DeviceManager]:
    with fakesd.setup() as device_manager:
        yield device_manager
