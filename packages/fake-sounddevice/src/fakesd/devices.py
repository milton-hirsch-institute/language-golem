# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import copy
import dataclasses
import math
import typing
from collections.abc import Callable
from typing import Any

import sounddevice
import sounddevice as sd

from fakesd import waves


class Device(typing.TypedDict):
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


class HostApi(typing.TypedDict):
    name: str
    devices: list[int]
    default_input_device: int
    default_output_device: int


class DeviceManager:
    @property
    def hostapi_count(self) -> int:
        return len(self.__hostapis)

    @property
    def device_count(self) -> int:
        return len(self.__devices)

    @property
    def default_input_device(self) -> int:
        return self.__default_input_device

    @property
    def default_output_device(self) -> int:
        return self.__default_output_device

    def __init__(self):
        self.__hostapis: list[HostApi] = []
        self.__devices: list[Device] = []
        self.__default_input_device = -1
        self.__default_output_device = -1

    def add_hostapi(self, name: str) -> int:
        hostapi = HostApi(
            name=name,
            devices=[],
            default_input_device=-1,
            default_output_device=-1,
        )
        self.__hostapis.append(hostapi)
        return len(self.__hostapis) - 1

    def add_device(
        self,
        name: str,
        hostapi: int,
        *,
        max_input_channels: int = 0,
        max_output_channels: int = 0,
        default_low_input_latency: float = 0.05,
        default_low_output_latency: float = 0.01,
        default_high_input_latency: float = 0.06,
        default_high_output_latency: float = 0.02,
        default_samplerate: float = 48000.0,
    ) -> int:
        if hostapi > len(self.__hostapis) - 1:
            raise ValueError("hostapi is not defined")
        if max_input_channels == 0 and max_output_channels == 0:
            raise ValueError("max_input_channels and max_output_channels cannot both be zero")

        device = Device(
            name=name,
            index=len(self.__devices),
            hostapi=hostapi,
            max_input_channels=max_input_channels,
            max_output_channels=max_output_channels,
            default_low_input_latency=default_low_input_latency,
            default_low_output_latency=default_low_output_latency,
            default_high_input_latency=default_high_input_latency,
            default_high_output_latency=default_high_output_latency,
            default_samplerate=default_samplerate,
        )

        self.__devices.append(device)

        hostapi_instance = self.__get_hostapi(hostapi)
        if device["max_input_channels"] > 0:
            if hostapi_instance["default_input_device"] < 0:
                hostapi_instance["default_input_device"] = device["index"]
            if self.__default_input_device < 0:
                self.__default_input_device = device["index"]

        if device["max_output_channels"] > 0:
            if hostapi_instance["default_output_device"] < 0:
                hostapi_instance["default_output_device"] = device["index"]
            if self.__default_output_device < 0:
                self.__default_output_device = device["index"]

        hostapi_instance["devices"].append(device["index"])

        return len(self.__devices) - 1

    def __get_hostapi(self, hostapi) -> HostApi:
        match hostapi:
            case int():
                try:
                    found_hostapi = self.__hostapis[hostapi]
                except IndexError:
                    raise sd.PortAudioError(f"Error querying host API {hostapi}") from None
                else:
                    return found_hostapi

            case _:
                raise TypeError(f"Unknown hostapi type: {repr(hostapi)}")

    def lookup_hostapi(self, hostapi) -> HostApi:
        return copy.copy(self.__get_hostapi(hostapi))

    def __get_device(self, device) -> Device:
        match device:
            case int():
                try:
                    found_device = self.__devices[device]
                except IndexError:
                    raise sd.PortAudioError(f"Error querying device {device}") from None
                else:
                    return copy.copy(found_device)
            case str():
                raise NotImplementedError("Lookup by name not supported")

            case _:
                raise TypeError(f"Unsupported device lookup type: {repr(device)}")

    def lookup_device(self, device) -> Device:
        return copy.copy(self.__get_device(device))

    def query_devices(self, device=None, kind=None):
        if kind not in ("input", "output", None):
            raise ValueError(f"Invalid kind: {kind!r}")
        if device is None and kind is None:
            return sd.DeviceList(self.query_devices(i) for i in range(len(self.__devices)))

        if not (device is None or kind is None):
            raise NotImplementedError("No support for both parameters")

        if device is not None:
            return self.lookup_device(device)

        match kind:
            case "input":
                return self.lookup_device(self.__default_input_device)

            case "output":
                return self.lookup_device(self.__default_output_device)

            case _:  # pragma: no cover
                raise AssertionError(f"Unknown device kind: {repr(kind)}")

    @classmethod
    def new_basic(cls, *, device_count: int = 4) -> typing.Self:
        manager = cls()
        hostapi = manager.add_hostapi("Test hostapi")

        for i in range(device_count):
            device_count = int(i / 3) + 1
            input_devices = 0
            output_devices = 0
            match i % 3:
                case 0:
                    name = f"Input device {i}"
                    input_devices = device_count
                case 1:
                    name = f"Output device {i}"
                    output_devices = device_count
                case 2:
                    name = f"Input/Output device {i}"
                    input_devices = device_count
                    output_devices = device_count
                case _ as device_config:  # pragma: no cover
                    raise AssertionError(f"Unknown device config: {device_config!r}")

            manager.add_device(
                name, hostapi, max_input_channels=input_devices, max_output_channels=output_devices
            )
        return manager


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
