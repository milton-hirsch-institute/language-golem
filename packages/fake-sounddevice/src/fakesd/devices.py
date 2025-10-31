# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

"""Fake audio device management and configuration for testing sounddevice."""

import copy
import typing

import sounddevice as sd


class Device(typing.TypedDict):
    """Typed dictionary representing an audio device.

    This is a specified version of the dictionaries returned by sounddevice
    query_devices().

    Attributes:
        name: Device name.
        index: Device index.
        hostapi: Host API index.
        max_input_channels: Maximum number of input channels.
        max_output_channels: Maximum number of output channels.
        default_low_input_latency: Default low input latency in seconds.
        default_low_output_latency: Default low output latency in seconds.
        default_high_input_latency: Default high input latency in seconds.
        default_high_output_latency: Default high output latency in seconds.
        default_samplerate: Default sample rate in Hz.
    """

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
    """Typed dictionary representing a host API.

    This is a specified version of the dictionaries returned by sounddevice
    query_hostapis().

    Attributes:
        name: Host API name.
        devices: List of device indices belonging to this host API.
        default_input_device: Index of default input device.
        default_output_device: Index of default output device.
    """

    name: str
    devices: list[int]
    default_input_device: int
    default_output_device: int


class DeviceManager:
    """Manages fake audio devices and host APIs for testing."""

    @property
    def hostapi_count(self) -> int:
        """Get the number of registered host APIs."""
        return len(self.__hostapis)

    @property
    def device_count(self) -> int:
        """Get the number of registered devices."""
        return len(self.__devices)

    @property
    def default_input_device(self) -> int:
        """Get the index of the default input device."""
        return self.__default_input_device

    @property
    def default_output_device(self) -> int:
        """Get the index of the default output device."""
        return self.__default_output_device

    def __init__(self):
        """Initialize a new DeviceManager."""
        self.__hostapis: list[HostApi] = []
        self.__devices: list[Device] = []
        self.__default_input_device = -1
        self.__default_output_device = -1

    def add_hostapi(self, name: str) -> int:
        """Add a new host API.

        Args:
            name: Name of the host API.

        Returns:
            Index of the newly created host API.
        """
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
        """Add a new audio device.

        Args:
            name: Device name.
            hostapi: Host API index for this device.
            max_input_channels: Maximum number of input channels.
            max_output_channels: Maximum number of output channels.
            default_low_input_latency: Default low input latency in seconds.
            default_low_output_latency: Default low output latency in seconds.
            default_high_input_latency: Default high input latency in seconds.
            default_high_output_latency: Default high output latency in seconds.
            default_samplerate: Default sample rate in Hz.

        Returns:
            Index of the newly created device.

        Raises:
            ValueError: If hostapi is not defined or both channel counts are zero.
        """
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
        """Look up a host API by index.

        Args:
            hostapi: Host API index.

        Returns:
            Copy of the host API dictionary.

        Raises:
            sd.PortAudioError: If the host API index is invalid.
            TypeError: If hostapi type is unsupported
        """
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
        """Look up a device by index.

        Args:
            device: Device index.

        Returns:
            Copy of the device dictionary.

        Raises:
            sd.PortAudioError: If the device index is invalid.
            TypeError: If device type is unsupported.
        """
        return copy.copy(self.__get_device(device))

    def query_devices(self, device=None, kind=None):
        """Query device information.

        Args:
            device: Device index or None to query all devices.
            kind: Device kind ("input", "output", or None).

        Returns:
            Device info or DeviceList of all devices.

        Raises:
            ValueError: If kind is invalid.
            NotImplementedError: If both device and kind are specified.
        """
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
        """Create a DeviceManager with a basic set of test devices.

        Args:
            device_count: Number of devices to create.

        Returns:
            New DeviceManager instance with test devices configured.
        """
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
