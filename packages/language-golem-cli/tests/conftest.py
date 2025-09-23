# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

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
def fake_query_devices(monkeypatch):
    def query_devices(device: int | None = None, kind: str | None = None) -> dict[str, Any]:
        assert not (device is None and kind is None)
        assert device == 8000 or kind == "input"
        return {
            "name": "Fake Microphone",
            "index": 8000,
            "hostapi": 0,
            "max_input_channels": 1,
            "max_output_channels": 0,
            "default_low_input_latency": 0.05,
            "default_low_output_latency": 0.01,
            "default_high_input_latency": 0.06,
            "default_high_output_latency": 0.02,
            "default_samplerate": 48000.0,
        }

    monkeypatch.setattr(sounddevice, "query_devices", query_devices)


@pytest.fixture
def fake_sounddevice(fake_query_devices, fake_input_stream):
    pass
