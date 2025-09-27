# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

"""Generate test data files for the fake-sounddevice package."""

import pathlib

from fakesd.waves import create_sawtooth_wave


def main():
    """Generate PCM test data files."""
    td = pathlib.Path(__file__).parent / "testdata"
    td.mkdir(parents=True, exist_ok=True)

    for bytes_per_frame in (1, 2, 4):
        for frequency in (0.5, 1.0, 2.0):
            for sample_rate in (44100, 24000):
                sample = create_sawtooth_wave(
                    frequency,
                    seconds=2.0,
                    sample_rate=sample_rate,
                    bytes_per_frame=bytes_per_frame,
                )
                output_file = td / f"sawtooth-{frequency}s-{bytes_per_frame}b-{sample_rate}Hz.pcm"
                output_file.write_bytes(sample)


if __name__ == "__main__":
    main()
