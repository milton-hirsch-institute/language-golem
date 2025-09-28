# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from typing import Any
from typing import cast

import pytest
import sounddevice as sd
from fakesd import streaming
from fakesd import waves


class TestFakeRawInputStream:
    @staticmethod
    @pytest.fixture
    def raw_input_stream() -> streaming.FakeRawInputStream:
        return streaming.FakeRawInputStream()

    @staticmethod
    def test_constructor():
        stream = streaming.FakeRawInputStream()

        assert stream._blocksize == 128  # pyright: ignore[reportPrivateUsage]
        assert stream._callback is None  # pyright: ignore[reportPrivateUsage]
        assert stream._channels == 1  # pyright: ignore[reportPrivateUsage]
        assert stream._device == 0  # pyright: ignore[reportPrivateUsage]
        assert stream._dtype == "int32"  # pyright: ignore[reportPrivateUsage]
        assert stream._latency == 0.1  # pyright: ignore[reportPrivateUsage]
        assert stream._ptr is streaming.FAKE_PTR  # pyright: ignore[reportPrivateUsage]
        assert stream._samplerate == 44100.0  # pyright: ignore[reportPrivateUsage]
        assert stream._samplesize == 4  # pyright: ignore[reportPrivateUsage]

        # properties
        assert stream.blocksize == 128
        assert stream.channels == 1
        assert stream.device == 0
        assert stream.dtype == "int32"
        assert stream.latency == 0.1
        assert stream.samplerate == 44100.0
        assert stream.samplesize == 4

    @staticmethod
    def test_unsupported_dtype():
        with pytest.raises(NotImplementedError, match="Unsupported dtype: 'float32'"):
            streaming.FakeRawInputStream(dtype="float32")

    @staticmethod
    def test_constructor_with_params():
        def callback():
            pass

        def finished_callback():
            pass

        stream = streaming.FakeRawInputStream(
            samplerate=48000.0,
            blocksize=512,
            device=1,
            channels=2,
            dtype="int16",
            latency=0.05,
            callback=cast(streaming.AudioInputCallback, callback),
            extra_settings={"test": True},
            finished_callback=finished_callback,
            clip_off=True,
            dither_off=False,
            never_drop_input=True,
            prime_output_buffers_using_stream_callback=False,
        )

        assert stream._blocksize == 512  # pyright: ignore[reportPrivateUsage]
        assert stream._callback is callback  # pyright: ignore[reportPrivateUsage]
        assert stream._channels == 2  # pyright: ignore[reportPrivateUsage]
        assert stream._device == 1  # pyright: ignore[reportPrivateUsage]
        assert stream._dtype == "int16"  # pyright: ignore[reportPrivateUsage]
        assert stream._latency == 0.05  # pyright: ignore[reportPrivateUsage]
        assert stream._ptr is streaming.FAKE_PTR  # pyright: ignore[reportPrivateUsage]
        assert stream._samplerate == 48000.0  # pyright: ignore[reportPrivateUsage]
        assert stream._samplesize == 4  # pyright: ignore[reportPrivateUsage]

        # properties
        assert stream.blocksize == 512
        assert stream.channels == 2
        assert stream.device == 1
        assert stream.dtype == "int16"
        assert stream.latency == 0.05
        assert stream.samplerate == 48000.0
        assert stream.samplesize == 4

    @staticmethod
    def test_active(raw_input_stream):
        assert not raw_input_stream.active
        raw_input_stream.start()
        assert raw_input_stream.active
        raw_input_stream.stop()
        assert not raw_input_stream.active
        raw_input_stream.start()
        assert raw_input_stream.active
        raw_input_stream.close()
        assert not raw_input_stream.active

    @staticmethod
    def test_stopped(raw_input_stream):
        assert raw_input_stream.stopped
        raw_input_stream.start()
        assert not raw_input_stream.stopped
        raw_input_stream.stop()
        assert raw_input_stream.stopped
        raw_input_stream.start()
        assert not raw_input_stream.stopped
        raw_input_stream.close()
        assert raw_input_stream.stopped

    @staticmethod
    def test_closed(raw_input_stream):
        assert not raw_input_stream.closed
        raw_input_stream.start()
        assert not raw_input_stream.closed
        raw_input_stream.stop()
        assert not raw_input_stream.closed
        raw_input_stream.start()
        assert not raw_input_stream.closed
        raw_input_stream.close()
        assert raw_input_stream.closed

    @staticmethod
    def test_time(raw_input_stream):
        assert raw_input_stream.time is None

    @staticmethod
    def test_cpu_load(raw_input_stream):
        assert raw_input_stream.cpu_load == 0.1

    @staticmethod
    def test_read_available(raw_input_stream):
        with pytest.raises(NotImplementedError):
            _ = raw_input_stream.read_available

    class TestStart:
        @staticmethod
        def test_multiple_starts(raw_input_stream):
            raw_input_stream.start()
            raw_input_stream.start()
            assert raw_input_stream.active

        @staticmethod
        def test_after_stop(raw_input_stream):
            raw_input_stream.start()
            raw_input_stream.stop()
            raw_input_stream.start()
            assert raw_input_stream.active

        @staticmethod
        def test_after_close(raw_input_stream):
            raw_input_stream.start()
            raw_input_stream.close()
            with pytest.raises(
                sd.PortAudioError, match=r"^Error starting stream pointer \[PaErrorCode -9988]$"
            ):
                raw_input_stream.start()
            assert not raw_input_stream.active

        @staticmethod
        def test_with_callback():
            blocks: list[tuple[bytes, float]] = []

            def callback(block: Any, frames: int, time: streaming.Time, status: sd.CallbackFlags):
                # Handle the end-of-input empty callback
                if frames == 0:
                    assert block == b""
                else:
                    assert frames == 4
                    assert len(block) == 8
                assert time.currentTime == 0
                assert time.outputBufferDacTime == 0
                assert isinstance(status, sd.CallbackFlags)
                blocks.append((block, time.inputBufferAdcTime))

            raw_input_stream = streaming.FakeRawInputStream(
                blocksize=4, dtype="int16", callback=callback
            )

            with raw_input_stream:
                assert len(blocks) == 22051

                for i, (_, timestamp) in enumerate(blocks):
                    assert timestamp == i / 2 / 44100.0

                for block, _ in blocks[:-1]:
                    assert len(block) == 8

                assert blocks[-1][0] == b""

                all_sound = b"".join([b for b, _ in blocks])
                assert all_sound == waves.create_sawtooth_wave(0.1, 2.0, 44100.0, 2)

    class TestStop:
        @staticmethod
        def test_multiple_stops(raw_input_stream):
            raw_input_stream.stop()
            raw_input_stream.stop()
            raw_input_stream.start()
            raw_input_stream.stop()
            raw_input_stream.stop()

        @staticmethod
        def test_do_not_ignore_errors(raw_input_stream):
            with pytest.raises(NotImplementedError):
                raw_input_stream.stop(ignore_errors=False)

    class TestClose:
        @staticmethod
        def test_ptr(raw_input_stream):
            raw_input_stream.close()
            assert raw_input_stream._ptr is None  # pyright: ignore[reportPrivateUsage]

        @staticmethod
        def test_do_not_ignore_errors(raw_input_stream):
            with pytest.raises(NotImplementedError):
                raw_input_stream.close(ignore_errors=False)


class TestFakeInputStream:
    @staticmethod
    def test_inheritance():
        """Test that FakeInputStream inherits from both sd.InputStream and FakeRawInputStream"""
        stream = streaming.FakeInputStream()

        # Test inheritance
        assert isinstance(stream, sd.InputStream)
        assert isinstance(stream, streaming.FakeRawInputStream)
        assert isinstance(stream, sd.RawInputStream)
