# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from typing import cast

import pytest
import sounddevice as sd
from fakesd import streaming
from fakesd import waves


class TestFakeCffiBuffer:
    @staticmethod
    @pytest.fixture
    def buf() -> streaming.FakeCffiBuffer:
        return streaming.FakeCffiBuffer(b"abcdef")

    class TestConstructor:
        @staticmethod
        def test_int():
            buf = streaming.FakeCffiBuffer(3)
            assert bytes(buf) == b"\0\0\0"

        @staticmethod
        def test_bytes():
            buf = streaming.FakeCffiBuffer(b"abc")
            assert bytes(buf) == b"abc"

        @staticmethod
        def test_bytearray():
            ba = bytearray(b"abc")
            buf = streaming.FakeCffiBuffer(ba)
            assert bytes(buf) == b"abc"
            buf[0] = ord("A")
            assert bytes(ba) == b"Abc"

    @staticmethod
    @pytest.mark.parametrize("param, expected", [(4, 4), (b"abcdef", 6), (bytearray(b"abc"), 3)])
    def test_len(param, expected):
        buf = streaming.FakeCffiBuffer(param)
        assert len(buf) == expected

    class TestGetItem:
        @staticmethod
        def test_int(buf):
            assert buf[2] == ord("c")

        @staticmethod
        def test_slice(buf):
            assert buf[2:4] == b"cd"

    class TestSetItem:
        @staticmethod
        def test_int(buf):
            buf[2] = ord("C")
            assert bytes(buf) == b"abCdef"

        @staticmethod
        def test_slice(buf):
            buf[2:4] = b"CD"
            assert bytes(buf) == b"abCDef"


class TestFakeStream:
    @staticmethod
    @pytest.fixture
    def stream() -> streaming.FakeStream:
        return streaming.FakeRawInputStream()

    @staticmethod
    def test_constructor():
        stream = streaming.FakeStream()

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
            streaming.FakeStream(dtype="float32")

    @staticmethod
    def test_constructor_with_params():
        def callback():
            pass

        def finished_callback():
            pass

        stream = streaming.FakeStream(
            samplerate=48000.0,
            blocksize=512,
            device=1,
            channels=2,
            dtype="int16",
            latency=0.05,
            callback=cast(streaming.AudioCallback, callback),
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
    def test_active(stream):
        assert not stream.active
        stream.start()
        assert stream.active
        stream.stop()
        assert not stream.active
        stream.start()
        assert stream.active
        stream.close()
        assert not stream.active

    @staticmethod
    def test_stopped(stream):
        assert stream.stopped
        stream.start()
        assert not stream.stopped
        stream.stop()
        assert stream.stopped
        stream.start()
        assert not stream.stopped
        stream.close()
        assert stream.stopped

    @staticmethod
    def test_closed(stream):
        assert not stream.closed
        stream.start()
        assert not stream.closed
        stream.stop()
        assert not stream.closed
        stream.start()
        assert not stream.closed
        stream.close()
        assert stream.closed

    @staticmethod
    def test_time(stream):
        assert stream.time is None

    @staticmethod
    def test_cpu_load(stream):
        assert stream.cpu_load == 0.1

    class TestStart:
        @staticmethod
        def test_multiple_starts(stream):
            stream.start()
            stream.start()
            assert stream.active

        @staticmethod
        def test_after_stop(stream):
            stream.start()
            stream.stop()
            stream.start()
            assert stream.active

        @staticmethod
        def test_after_close(stream):
            stream.start()
            stream.close()
            with pytest.raises(
                sd.PortAudioError, match=r"^Error starting stream pointer \[PaErrorCode -9988]$"
            ):
                stream.start()
            assert not stream.active

    class TestStop:
        @staticmethod
        def test_multiple_stops(stream):
            stream.stop()
            stream.stop()
            stream.start()
            stream.stop()
            stream.stop()

        @staticmethod
        def test_do_not_ignore_errors(stream):
            with pytest.raises(NotImplementedError):
                stream.stop(ignore_errors=False)

    class TestClose:
        @staticmethod
        def test_ptr(stream):
            stream.close()
            assert stream._ptr is None  # pyright: ignore[reportPrivateUsage]

        @staticmethod
        def test_do_not_ignore_errors(stream):
            with pytest.raises(NotImplementedError):
                stream.close(ignore_errors=False)


class TestFakeRawInputStream:
    @staticmethod
    @pytest.fixture
    def raw_input_stream() -> streaming.FakeRawInputStream:
        return streaming.FakeRawInputStream()

    @staticmethod
    def test_read_available(raw_input_stream):
        with pytest.raises(NotImplementedError):
            _ = raw_input_stream.read_available

    class TestStart:
        @staticmethod
        def test_with_callback():
            blocks: list[tuple[bytes, float]] = []

            def callback(
                block: streaming.CffiBuffer,
                frames: int,
                time: streaming.Time,
                status: sd.CallbackFlags,
            ):
                # Handle the end-of-input empty callback
                if frames == 0:
                    assert bytes(block) == b""
                else:
                    assert frames == 4
                    assert len(block) == 8
                assert time.currentTime == 0
                assert time.outputBufferDacTime == 0
                assert isinstance(status, sd.CallbackFlags)
                blocks.append((bytes(block), time.inputBufferAdcTime))

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
