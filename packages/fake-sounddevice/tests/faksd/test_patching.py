# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import sounddevice as sd
from fakesd import devices
from fakesd import patching
from fakesd import streaming


class TestSetup:
    @staticmethod
    def do_patch_setup_test(init_device_manager: devices.DeviceManager | None, expected_devices):
        original_query_devices = sd.query_devices
        original_input_stream = sd.InputStream

        with patching.setup(init_device_manager) as device_manager:
            # Check symbols
            assert sd.query_devices == device_manager.query_devices
            assert sd.RawInputStream is streaming.FakeRawInputStream

            # Check device manager
            assert device_manager.device_count == expected_devices
            if init_device_manager is not None:
                assert device_manager is init_device_manager

        # Should be restored after context exit
        assert sd.query_devices is original_query_devices
        assert sd.InputStream is original_input_stream

    @staticmethod
    def test_default_manager():
        """Test fake_sounddevice with default device manager."""
        TestSetup.do_patch_setup_test(None, 4)

    @staticmethod
    def test_custom_manager():
        """Test fake_sounddevice with custom device manager."""
        TestSetup.do_patch_setup_test(devices.DeviceManager.new_basic(device_count=8), 8)

    @staticmethod
    def test_nested_contexts():
        """Test nested fake_sounddevice contexts."""
        original_query_devices = sd.query_devices

        manager1 = devices.DeviceManager.new_basic(device_count=3)
        manager2 = devices.DeviceManager.new_basic(device_count=5)

        with patching.setup(manager1):
            devices_outer = sd.query_devices()
            assert len(devices_outer) == 3

            with patching.setup(manager2):
                devices_inner = sd.query_devices()
                assert len(devices_inner) == 5

            # Should restore to outer context
            devices_restored = sd.query_devices()
            assert len(devices_restored) == 3

        # Should be fully restored
        assert sd.query_devices is original_query_devices
