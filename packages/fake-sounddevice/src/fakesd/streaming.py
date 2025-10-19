# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import math
import typing
from collections.abc import Callable

import sounddevice
import sounddevice as sd

from fakesd import waves

FAKE_PTR = object()

DTYPE_TO_BYTE_SIZE = {
    "int8": 1,
    "int16": 2,
    "int24": 3,
    "int32": 4,
}


class Time(typing.Protocol):
    currentTime: float
    inputBufferAdcTime: float
    outputBufferDacTime: float


@dataclasses.dataclass
class TimeStruct:
    currentTime: float
    inputBufferAdcTime: float
    outputBufferDacTime: float


class CffiBuffer(typing.Protocol):
    def __len__(self) -> int: ...

    @typing.overload
    def __getitem__(self, item: int) -> int: ...

    @typing.overload
    def __getitem__(self, item: slice) -> bytes: ...

    def __getitem__(self, item: int | slice) -> int | bytes: ...

    @typing.overload
    def __setitem__(self, key: int, value: int): ...

    @typing.overload
    def __setitem__(self, key: slice, value: bytes): ...

    def __setitem__(self, key: int | slice, value: int | bytes): ...

    def __bytes__(self) -> bytes: ...


class FakeCffiBuffer:
    def __init__(self, param: int | bytes | bytearray):
        if isinstance(param, bytearray):
            self.__buffer = param
        else:
            self.__buffer = bytearray(param)

    def __len__(self) -> int:
        return len(self.__buffer)

    @typing.overload
    def __getitem__(self, item: int) -> int: ...

    @typing.overload
    def __getitem__(self, item: slice) -> bytes: ...

    def __getitem__(self, item: int | slice) -> int | bytes:
        if isinstance(item, slice):
            return bytes(self.__buffer[item])
        else:
            return self.__buffer[item]

    @typing.overload
    def __setitem__(self, key: int, value: int): ...

    @typing.overload
    def __setitem__(self, key: slice, value: bytes): ...

    def __setitem__(self, key: int | slice, value: int | bytes):
        self.__buffer[key] = value  # pyright: ignore[reportCallIssue, reportArgumentType]

    def __bytes__(self) -> bytes:
        return bytes(self.__buffer)


type AudioCallback = Callable[[CffiBuffer, int, Time, sd.CallbackFlags], None]


class FakeStream(sounddevice._StreamBase):  # pyright: ignore[reportPrivateUsage]
    @property
    def active(self):
        if self.closed:
            return False
        return self.__active

    @property
    def stopped(self):
        return not self.active

    @property
    def closed(self):
        return self._ptr is None

    @property
    def time(self):
        return self.__time

    @property
    def cpu_load(self):
        return self.__cpu_load

    def __init__(
        self,
        samplerate: float | None = None,
        blocksize: int | None = None,
        device: int | None = None,
        channels: int | None = None,
        dtype: str | None = None,
        latency: float | None = None,
        extra_settings=None,
        callback: AudioCallback | None = None,
        finished_callback=None,
        clip_off=None,
        dither_off=None,
        never_drop_input=None,
        prime_output_buffers_using_stream_callback=None,
    ):
        if dtype is None:
            dtype = "int32"
        if dtype not in DTYPE_TO_BYTE_SIZE:
            raise NotImplementedError(f"Unsupported dtype: {repr(dtype)}")

        # Store constructor parameters without calling parent constructor
        # to avoid hardware interaction
        self._samplerate = samplerate or 44100.0
        self._blocksize = blocksize or 128
        self._device = device or 0
        self._channels = channels or 1
        self._dtype = dtype or "float32"
        self._latency = latency or 0.1
        self.__extra_settings = extra_settings
        self._callback = callback
        self.__finished_callback = finished_callback
        self.__clip_off = clip_off
        self.__dither_off = dither_off
        self.__never_drop_input = never_drop_input
        self.__prime_output_buffers_using_stream_callback = (
            prime_output_buffers_using_stream_callback
        )

        # Initialize fake state
        self.__active = False
        self._ptr = FAKE_PTR  # Fake pointer
        self._samplesize = 4  # 4 bytes for float32
        self.__time = None
        self.__cpu_load = 0.1

    def start(self):
        if self._ptr is not FAKE_PTR:
            raise sd.PortAudioError("Error starting stream pointer [PaErrorCode -9988]")
        self.__active = True

    def stop(self, ignore_errors: bool = True):
        if not ignore_errors:
            raise NotImplementedError()
        self.__active = False

    def close(self, ignore_errors: bool = True):
        if not ignore_errors:
            raise NotImplementedError()
        self._ptr = None


class FakeRawInputStream(FakeStream, sd.RawInputStream):
    @property
    def read_available(self):
        raise NotImplementedError()

    def start(self):
        super().start()

        if self._callback is not None:
            # Generate a whole bunch of audio - 2 seconds worth
            bytes_per_frame = DTYPE_TO_BYTE_SIZE[self._dtype]
            audio = waves.create_sawtooth_wave(0.1, 2.0, self._samplerate, bytes_per_frame)

            bytes_per_block = bytes_per_frame * self._blocksize
            block_count = int(math.ceil(len(audio) / bytes_per_block))

            for index in range(block_count):
                start = index * bytes_per_block
                block = FakeCffiBuffer(audio[start : start + bytes_per_block])
                current_time = (index / float(bytes_per_frame)) / self._samplerate
                time_struct = TimeStruct(0, current_time, 0)
                self._callback(block, self._blocksize, time_struct, sounddevice.CallbackFlags())

            # Add an empty callback for use by some tests to know when end of input occurs
            current_time = (block_count / float(bytes_per_frame)) / self._samplerate
            time_struct = TimeStruct(0, current_time, 0)
            self._callback(FakeCffiBuffer(b""), 0, time_struct, sounddevice.CallbackFlags())
