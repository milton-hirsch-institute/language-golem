# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import pytest
import sounddevice as sd
from fakesd.devices import DeviceManager


class TestDeviceManager:
    @staticmethod
    def test_constructor(device_manager):
        assert device_manager.default_input_device == -1
        assert device_manager.default_output_device == -1
        assert device_manager.device_count == 0
        assert device_manager.hostapi_count == 0

    @staticmethod
    @pytest.fixture
    def device_manager() -> DeviceManager:
        return DeviceManager()

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

    @staticmethod
    def test_add_device(device_manager):
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
        assert hostapi_instance["default_input_device"] == 0
        assert hostapi_instance["default_output_device"] == 1


class TestLookupHostapi:
    @staticmethod
    @pytest.fixture
    def device_manager() -> DeviceManager:
        dm = DeviceManager()
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
    def device_manager() -> DeviceManager:
        dm = DeviceManager()
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


class TestQueryDevices:
    @staticmethod
    @pytest.fixture
    def device_manager() -> DeviceManager:
        dm = DeviceManager()
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
