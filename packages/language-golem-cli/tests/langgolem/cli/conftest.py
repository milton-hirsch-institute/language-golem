# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0
import pathlib

import pytest
from click import testing
from fakesd import waves
from langgolem.audio import devices


@pytest.fixture
def runner() -> testing.CliRunner:
    return testing.CliRunner()


@pytest.fixture
def audio_content() -> bytes:
    return bytes(waves.create_sawtooth_wave(400, 10, devices.AUDIO_SAMPLE_RATE, 2))


@pytest.fixture
def audio_file(tmp_path, audio_content) -> pathlib.Path:
    audio_path = tmp_path / "audio.pcm"
    audio_path.write_bytes(audio_content)
    return audio_path
