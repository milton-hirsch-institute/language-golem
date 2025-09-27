# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0


def create_sawtooth_wave(
    period: float, seconds: float, sample_rate: float, bytes_per_frame: int, start: float = 0.0
) -> bytearray:
    """Create a sawtooth wave as a bytearray.

    Args:
        period: Frequency of the wave in Hz
        seconds: Duration of the wave in seconds
        sample_rate: Sample rate in samples per second
        bytes_per_frame: Number of bytes per sample frame
        start: Starting phase offset in seconds

    Returns:
        bytearray containing the sawtooth wave data
    """

    total_samples = int(seconds * sample_rate)
    buffer = bytearray(total_samples * bytes_per_frame)
    max_value = (1 << (bytes_per_frame * 8 - 1)) - 1
    start_index = int(start * sample_rate)

    for i in range(total_samples):
        time_seconds = (i + start_index) / sample_rate
        phase = (time_seconds * period) % 1.0
        amplitude = 2.0 * phase - 1.0

        sample_value = int(amplitude * max_value)
        byte_position = i * bytes_per_frame
        value_bytes = sample_value.to_bytes(bytes_per_frame, byteorder="little", signed=True)
        buffer[byte_position : byte_position + bytes_per_frame] = value_bytes

    return buffer
