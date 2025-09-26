# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import pytest
import sounddevice as sd
from fakesd import devices


class TestDeviceManager:
    @staticmethod
    def test_constructor(device_manager):
        assert device_manager.default_input_device == -1
        assert device_manager.default_output_device == -1
        assert device_manager.device_count == 0
        assert device_manager.hostapi_count == 0

    @staticmethod
    @pytest.fixture
    def device_manager() -> devices.DeviceManager:
        return devices.DeviceManager()

    @staticmethod
    def test_add_hostapi(device_manager):
        assert device_manager.add_hostapi("host 1") == 0
        assert device_manager.add_hostapi("host 2") == 1

        assert device_manager.hostapi_count == 2

        assert device_manager.lookup_hostapi(0) == {
            "name": "host 1",
            "devices": [],
            "default_input_device": -1,
            "default_output_device": -1,
        }
        assert device_manager.lookup_hostapi(1) == {
            "name": "host 2",
            "devices": [],
            "default_input_device": -1,
            "default_output_device": -1,
        }

    class TestAddDevice:
        @staticmethod
        @pytest.fixture
        def device_manager() -> devices.DeviceManager:
            return devices.DeviceManager()

        @staticmethod
        def test_success(device_manager):
            hostapi = device_manager.add_hostapi("host 1")

            assert device_manager.add_device("device 1", hostapi, max_input_channels=2) == 0
            assert device_manager.add_device("device 2", hostapi, max_output_channels=2) == 1

            assert device_manager.device_count == 2

            device1 = device_manager.lookup_device(0)
            assert device1["name"] == "device 1"
            assert device1["index"] == 0
            assert device1["hostapi"] == hostapi
            assert device1["max_input_channels"] == 2
            assert device1["max_output_channels"] == 0
            assert device1["default_low_input_latency"] == 0.05
            assert device1["default_low_output_latency"] == 0.01
            assert device1["default_high_input_latency"] == 0.06
            assert device1["default_high_output_latency"] == 0.02
            assert device1["default_samplerate"] == 48000.0

            device2 = device_manager.lookup_device(1)
            assert device2["name"] == "device 2"
            assert device2["index"] == 1
            assert device2["hostapi"] == hostapi
            assert device2["max_input_channels"] == 0
            assert device2["max_output_channels"] == 2
            assert device2["default_low_input_latency"] == 0.05
            assert device2["default_low_output_latency"] == 0.01
            assert device2["default_high_input_latency"] == 0.06
            assert device2["default_high_output_latency"] == 0.02
            assert device2["default_samplerate"] == 48000.0

            assert device_manager.default_input_device == 0
            assert device_manager.default_output_device == 1

            hostapi_instance = device_manager.lookup_hostapi(hostapi)
            assert hostapi_instance == {
                "name": "host 1",
                "devices": [0, 1],
                "default_input_device": 0,
                "default_output_device": 1,
            }

        @staticmethod
        def test_invalid_hostapi(device_manager):
            with pytest.raises(ValueError, match="hostapi is not defined"):
                device_manager.add_device("device", 5, max_input_channels=2)

        @staticmethod
        def test_both_zero_channels(device_manager):
            hostapi = device_manager.add_hostapi("host 1")

            with pytest.raises(
                ValueError, match="max_input_channels and max_output_channels cannot both be zero"
            ):
                device_manager.add_device("device", hostapi)


class TestLookupHostapi:
    @staticmethod
    @pytest.fixture
    def device_manager() -> devices.DeviceManager:
        dm = devices.DeviceManager()
        dm.add_hostapi("host 1")
        dm.add_hostapi("host 2")
        return dm

    @staticmethod
    def test_int_not_found(device_manager):
        with pytest.raises(sd.PortAudioError, match="Error querying host API 5"):
            device_manager.lookup_hostapi(5)

    @staticmethod
    def test_int_found(device_manager):
        result1 = device_manager.lookup_hostapi(0)
        assert result1["name"] == "host 1"
        assert result1["devices"] == []
        assert result1["default_input_device"] == -1
        assert result1["default_output_device"] == -1

        result2 = device_manager.lookup_hostapi(1)
        assert result2["name"] == "host 2"
        assert result2["devices"] == []
        assert result2["default_input_device"] == -1
        assert result2["default_output_device"] == -1

    @staticmethod
    def test_str(device_manager):
        with pytest.raises(TypeError, match="Unknown hostapi type: 'host 1'"):
            device_manager.lookup_hostapi("host 1")

    @staticmethod
    def test_unpexected_type(device_manager):
        with pytest.raises(TypeError, match="Unknown hostapi type: None"):
            device_manager.lookup_hostapi(None)

    @staticmethod
    def test_not_same(device_manager):
        result1 = device_manager.lookup_hostapi(0)
        result2 = device_manager.lookup_hostapi(0)

        # Should be equal but not the same object
        assert result1 == result2
        assert result1 is not result2


class TestLookupDevice:
    @staticmethod
    @pytest.fixture
    def device_manager() -> devices.DeviceManager:
        dm = devices.DeviceManager()
        hostapi = dm.add_hostapi("host 1")
        dm.add_device("device 1", hostapi, max_input_channels=2)
        dm.add_device("device 2", hostapi, max_output_channels=2)
        return dm

    @staticmethod
    def test_int_not_found(device_manager):
        with pytest.raises(sd.PortAudioError, match="Error querying device"):
            device_manager.lookup_device(5)

    @staticmethod
    def test_int_found(device_manager):
        result1 = device_manager.lookup_device(0)
        assert result1["name"] == "device 1"
        assert result1["index"] == 0
        assert result1["hostapi"] == 0
        assert result1["max_input_channels"] == 2
        assert result1["max_output_channels"] == 0
        assert result1["default_low_input_latency"] == 0.05
        assert result1["default_low_output_latency"] == 0.01
        assert result1["default_high_input_latency"] == 0.06
        assert result1["default_high_output_latency"] == 0.02
        assert result1["default_samplerate"] == 48000.0

        result2 = device_manager.lookup_device(1)
        assert result2["name"] == "device 2"
        assert result2["index"] == 1
        assert result2["hostapi"] == 0
        assert result2["max_input_channels"] == 0
        assert result2["max_output_channels"] == 2
        assert result2["default_low_input_latency"] == 0.05
        assert result2["default_low_output_latency"] == 0.01
        assert result2["default_high_input_latency"] == 0.06
        assert result2["default_high_output_latency"] == 0.02
        assert result2["default_samplerate"] == 48000.0

    @staticmethod
    def test_str(device_manager):
        with pytest.raises(NotImplementedError, match="Lookup by name not supported"):
            device_manager.lookup_device("device 1")

    @staticmethod
    def test_unexpected_type(device_manager):
        with pytest.raises(TypeError, match="Unsupported device lookup type: None"):
            device_manager.lookup_device(None)

    @staticmethod
    def test_not_same(device_manager):
        result1 = device_manager.lookup_device(0)
        result2 = device_manager.lookup_device(0)

        # Should be equal but not the same object
        assert result1 == result2
        assert result1 is not result2

        # Modifying one shouldn't affect the other
        result1["name"] = "modified"
        assert result2["name"] == "device 1"


class TestNewBasic:
    @staticmethod
    def test_numerous_devices():
        manager = devices.DeviceManager.new_basic(device_count=6)

        assert manager.device_count == 6
        assert manager.hostapi_count == 1

        # Check hostapi
        hostapi = manager.lookup_hostapi(0)
        assert hostapi == {
            "name": "Test hostapi",
            "devices": [0, 1, 2, 3, 4, 5],
            "default_input_device": 0,
            "default_output_device": 1,
        }

        # Check devices
        expected_devices = [
            {"name": "Input device 0", "max_input_channels": 1, "max_output_channels": 0},
            {"name": "Output device 1", "max_input_channels": 0, "max_output_channels": 1},
            {"name": "Input/Output device 2", "max_input_channels": 1, "max_output_channels": 1},
            {"name": "Input device 3", "max_input_channels": 2, "max_output_channels": 0},
            {"name": "Output device 4", "max_input_channels": 0, "max_output_channels": 2},
            {"name": "Input/Output device 5", "max_input_channels": 2, "max_output_channels": 2},
        ]

        for i, expected in enumerate(expected_devices):
            device = manager.lookup_device(i)
            assert device["name"] == expected["name"]
            assert device["max_input_channels"] == expected["max_input_channels"]
            assert device["max_output_channels"] == expected["max_output_channels"]


class TestQueryDevices:
    @staticmethod
    @pytest.fixture
    def device_manager() -> devices.DeviceManager:
        dm = devices.DeviceManager()
        hostapi = dm.add_hostapi("host 1")
        dm.add_device("input device", hostapi, max_input_channels=2)
        dm.add_device("output device", hostapi, max_output_channels=2)
        return dm

    @staticmethod
    def test_invalid_kind(device_manager):
        with pytest.raises(ValueError, match="Invalid kind: 'invalid'"):
            device_manager.query_devices(kind="invalid")

    @staticmethod
    def test_no_parameters(device_manager):
        result = device_manager.query_devices()
        assert isinstance(result, sd.DeviceList)
        device1, device2 = result
        assert device1 == device_manager.lookup_device(0)
        assert device2 == device_manager.lookup_device(1)

    @staticmethod
    def test_both_parameters(device_manager):
        with pytest.raises(NotImplementedError, match="No support for both parameters"):
            device_manager.query_devices(device=0, kind="input")

    @staticmethod
    def test_device_lookup(device_manager):
        assert device_manager.query_devices(device=0) == device_manager.lookup_device(0)

    @staticmethod
    def test_input_lookup(device_manager):
        assert device_manager.query_devices(kind="input") == device_manager.lookup_device(0)

    @staticmethod
    def test_output_lookup(device_manager):
        assert device_manager.query_devices(kind="output") == device_manager.lookup_device(1)

    @staticmethod
    def test_not_same(device_manager):
        result1 = device_manager.query_devices(device=0)
        result2 = device_manager.query_devices(device=0)

        # Should be equal but not the same object
        assert result1 == result2
        assert result1 is not result2


class TestFakeInputStream:
    @staticmethod
    @pytest.fixture
    def input_stream() -> devices.FakeInputStream:
        return devices.FakeInputStream()

    @staticmethod
    def test_constructor():
        stream = devices.FakeInputStream()

        assert stream._blocksize == 1024  # pyright: ignore[reportPrivateUsage]
        assert stream._callback is None  # pyright: ignore[reportPrivateUsage]
        assert stream._channels == 1  # pyright: ignore[reportPrivateUsage]
        assert stream._device == 0  # pyright: ignore[reportPrivateUsage]
        assert stream._dtype == "float32"  # pyright: ignore[reportPrivateUsage]
        assert stream._latency == 0.1  # pyright: ignore[reportPrivateUsage]
        assert stream._ptr is devices.FAKE_PTR  # pyright: ignore[reportPrivateUsage]
        assert stream._samplerate == 44100.0  # pyright: ignore[reportPrivateUsage]
        assert stream._samplesize == 4  # pyright: ignore[reportPrivateUsage]

        # properties
        assert stream.blocksize == 1024
        assert stream.channels == 1
        assert stream.device == 0
        assert stream.dtype == "float32"
        assert stream.latency == 0.1
        assert stream.samplerate == 44100.0
        assert stream.samplesize == 4

    @staticmethod
    def test_constructor_with_params():
        def callback():
            pass

        def finished_callback():
            pass

        stream = devices.FakeInputStream(
            samplerate=48000.0,
            blocksize=512,
            device=1,
            channels=2,
            dtype="int16",
            latency=0.05,
            callback=callback,
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
        assert stream._ptr is devices.FAKE_PTR  # pyright: ignore[reportPrivateUsage]
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
    def test_active(input_stream):
        assert not input_stream.active
        input_stream.start()
        assert input_stream.active
        input_stream.stop()
        assert not input_stream.active
        input_stream.start()
        assert input_stream.active
        input_stream.close()
        assert not input_stream.active

    @staticmethod
    def test_stopped(input_stream):
        assert input_stream.stopped
        input_stream.start()
        assert not input_stream.stopped
        input_stream.stop()
        assert input_stream.stopped
        input_stream.start()
        assert not input_stream.stopped
        input_stream.close()
        assert input_stream.stopped

    @staticmethod
    def test_closed(input_stream):
        assert not input_stream.closed
        input_stream.start()
        assert not input_stream.closed
        input_stream.stop()
        assert not input_stream.closed
        input_stream.start()
        assert not input_stream.closed
        input_stream.close()
        assert input_stream.closed

    @staticmethod
    def test_time(input_stream):
        assert input_stream.time is None

    @staticmethod
    def test_cpu_load(input_stream):
        assert input_stream.cpu_load == 0.1

    @staticmethod
    def test_read_available(input_stream):
        with pytest.raises(NotImplementedError):
            _ = input_stream.read_available

    class TestStart:
        @staticmethod
        def test_multiple_starts(input_stream):
            input_stream.start()
            input_stream.start()
            assert input_stream.active

        @staticmethod
        def test_after_stop(input_stream):
            input_stream.start()
            input_stream.stop()
            input_stream.start()
            assert input_stream.active

        @staticmethod
        def test_after_close(input_stream):
            input_stream.start()
            input_stream.close()
            with pytest.raises(
                sd.PortAudioError, match=r"^Error starting stream pointer \[PaErrorCode -9988]$"
            ):
                input_stream.start()
            assert not input_stream.active

    class TestStop:
        @staticmethod
        def test_multiple_stops(input_stream):
            input_stream.stop()
            input_stream.stop()
            input_stream.start()
            input_stream.stop()
            input_stream.stop()

        @staticmethod
        def test_do_not_ignore_errors(input_stream):
            with pytest.raises(NotImplementedError):
                input_stream.stop(ignore_errors=False)

    class TestClose:
        @staticmethod
        def test_ptr(input_stream):
            input_stream.close()
            assert input_stream._ptr is None  # pyright: ignore[reportPrivateUsage]

        @staticmethod
        def test_do_not_ignore_errors(input_stream):
            with pytest.raises(NotImplementedError):
                input_stream.close(ignore_errors=False)
