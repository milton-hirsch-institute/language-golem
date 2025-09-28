# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import math
import typing
from collections.abc import Callable
from typing import Any

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


type AudioInputCallback = Callable[[Any, int, Time, sd.CallbackFlags], None]


class FakeRawInputStream(sd.RawInputStream):
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

    @property
    def read_available(self):
        raise NotImplementedError()

    def __init__(
        self,
        samplerate: float | None = None,
        blocksize: int | None = None,
        device: int | None = None,
        channels: int | None = None,
        dtype: str | None = None,
        latency: float | None = None,
        extra_settings=None,
        callback: AudioInputCallback | None = None,
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

        if self._callback is not None:
            # Generate a whole bunch of audio - 2 seconds worth
            bytes_per_frame = DTYPE_TO_BYTE_SIZE[self._dtype]
            audio = waves.create_sawtooth_wave(0.1, 2.0, self._samplerate, bytes_per_frame)

            bytes_per_block = bytes_per_frame * self._blocksize
            block_count = int(math.ceil(len(audio) / bytes_per_block))

            for index in range(block_count):
                start = index * bytes_per_block
                block = audio[start : start + bytes_per_block]
                current_time = (index / float(bytes_per_frame)) / self._samplerate
                time_struct = TimeStruct(0, current_time, 0)
                self._callback(block, self._blocksize, time_struct, sounddevice.CallbackFlags())

            # Add an empty callback for use by some tests to know when end of input occurs
            current_time = (block_count / float(bytes_per_frame)) / self._samplerate
            time_struct = TimeStruct(0, current_time, 0)
            self._callback(b"", 0, time_struct, sounddevice.CallbackFlags())

    def stop(self, ignore_errors: bool = True):
        if not ignore_errors:
            raise NotImplementedError()
        self.__active = False

    def close(self, ignore_errors: bool = True):
        if not ignore_errors:
            raise NotImplementedError()
        self._ptr = None


class FakeInputStream(FakeRawInputStream, sd.InputStream):
    def __init__(
        self,
        samplerate: float | None = None,
        blocksize: int | None = None,
        device: int | None = None,
        channels: int | None = None,
        dtype: str | None = None,
        latency: float | None = None,
        extra_settings=None,
        callback: AudioInputCallback | None = None,
        finished_callback=None,
        clip_off=None,
        dither_off=None,
        never_drop_input=None,
        prime_output_buffers_using_stream_callback=None,
    ):
        # Call FakeRawInputStream constructor to initialize fake stream
        FakeRawInputStream.__init__(
            self,
            samplerate=samplerate,
            blocksize=blocksize,
            device=device,
            channels=channels,
            dtype=dtype,
            latency=latency,
            extra_settings=extra_settings,
            callback=callback,
            finished_callback=finished_callback,
            clip_off=clip_off,
            dither_off=dither_off,
            never_drop_input=never_drop_input,
            prime_output_buffers_using_stream_callback=prime_output_buffers_using_stream_callback,
        )
