# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import pytest
from langgolem.audio import devices


@pytest.fixture(autouse=True)
def enable_fake_soundevice(fake_sd):
    pass


def test_default_audio_device():
    audio_device = devices.default_input_device()
    assert audio_device == devices.AudioDevice(
        name="Input device 0",
        index=0,
        hostapi=0,
        max_input_channels=1,
        max_output_channels=0,
        default_low_input_latency=0.05,
        default_low_output_latency=0.01,
        default_high_input_latency=0.06,
        default_high_output_latency=0.02,
        default_samplerate=48000.0,
    )


def test_default_input_stream():
    def callback(*args):
        pytest.fail("Unexpected callback")

    input_stream = devices.default_input_stream(callback)
    assert input_stream.samplerate == devices.AUDIO_SAMPLE_RATE
    assert input_stream.dtype == "int16"
    assert input_stream.channels == 1
    assert input_stream.device == 0
    assert input_stream._callback == callback  # pyright: ignore[reportPrivateUsage]
