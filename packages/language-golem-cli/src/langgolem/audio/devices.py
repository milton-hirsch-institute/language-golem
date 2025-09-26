# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import dataclasses
from collections.abc import Callable
from typing import Any

import sounddevice

AUDIO_SAMPLE_RATE = 24000.0

type AudioInputCallback = Callable[[Any, int, Any, sounddevice.CallbackFlags], None]


@dataclasses.dataclass(frozen=True)
class AudioDevice:
    name: str
    index: int
    hostapi: int
    max_input_channels: int
    max_output_channels: int
    default_low_input_latency: float
    default_low_output_latency: float
    default_high_input_latency: float
    default_high_output_latency: float
    default_samplerate: float


def default_input_device() -> AudioDevice:
    return AudioDevice(**sounddevice.query_devices(kind="input"))


def default_input_stream(callback: AudioInputCallback) -> sounddevice.InputStream:
    input_device = default_input_device()
    return sounddevice.InputStream(
        samplerate=AUDIO_SAMPLE_RATE,
        channels=1,
        device=input_device.index,
        callback=callback,
        dtype="int16",
    )
