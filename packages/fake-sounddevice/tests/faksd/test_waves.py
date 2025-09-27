# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import pathlib

import pytest
from fakesd import waves


@pytest.fixture(scope="session")
def sawtooth_waves():
    """Load all sawtooth wave test data into a 3D array,

    Array is indexed by [period, bytes_per_frame, sample_rate]."""
    testdata_dir = pathlib.Path(__file__).parent / "testdata"

    wave_data: dict[tuple[float, int, float], bytes] = {}

    for bytes_per_frame in (1, 2, 4):
        for period in (0.5, 1.0, 2.0):
            for sample_rate in (44100, 24000):
                filename = f"sawtooth-{period}s-{bytes_per_frame}b-{sample_rate}Hz.pcm"
                file_path = testdata_dir / filename
                wave_data[period, bytes_per_frame, sample_rate] = file_path.read_bytes()

    return wave_data


@pytest.fixture(params=[0.5, 1.0, 2.0])
def period(request):
    """Period values for parametrized tests."""
    return request.param


@pytest.fixture(params=[1, 2, 4])
def bytes_per_frame(request):
    """Bytes per frame values for parametrized tests."""
    return request.param


@pytest.fixture(params=[44100, 24000])
def sample_rate(request):
    """Sample rate values for parametrized tests."""
    return request.param


@pytest.fixture
def sawtooth_wave(sawtooth_waves, period, bytes_per_frame, sample_rate):
    """Return a wave based on parametrized period, bytes_per_frame, and sample_rate fixtures."""
    return sawtooth_waves[period, bytes_per_frame, sample_rate]


class TestCreateSawtoothWave:
    """Test class for create_sawtooth_wave function."""

    @staticmethod
    def test_default_matches_fixture(sawtooth_wave, period, bytes_per_frame, sample_rate):
        """Test create_sawtooth_wave with default start value matches fixture data."""
        result = waves.create_sawtooth_wave(
            period=period,
            seconds=2.0,
            sample_rate=float(sample_rate),
            bytes_per_frame=bytes_per_frame,
        )

        assert isinstance(result, bytearray)

        assert bytes(result) == sawtooth_wave

    @staticmethod
    def test_start_offset(sawtooth_wave, period, bytes_per_frame, sample_rate):
        """Test create_sawtooth_wave with custom start value > 0."""
        result = bytes(
            waves.create_sawtooth_wave(
                period=period,
                seconds=1,
                sample_rate=float(sample_rate),
                bytes_per_frame=bytes_per_frame,
                start=0.2,
            )
        )

        # The result with start=0.2 should match a subarray of the fixture data
        # starting at 0.2 seconds offset
        offset_samples = int(0.2 * sample_rate) * bytes_per_frame
        expected_subarray = sawtooth_wave[offset_samples : offset_samples + len(result)]
        assert result == expected_subarray
