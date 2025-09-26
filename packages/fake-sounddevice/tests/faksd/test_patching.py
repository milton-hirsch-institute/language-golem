# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import sounddevice as sd
from fakesd import devices
from fakesd import patching


class TestSetup:
    @staticmethod
    def test_default_manager():
        """Test fake_sounddevice with default device manager."""
        original_query_devices = sd.query_devices

        with patching.setup() as device_manager:
            assert sd.query_devices is not original_query_devices
            assert device_manager.device_count == 4

        # Should be restored after context exit
        assert sd.query_devices is original_query_devices

    @staticmethod
    def test_custom_manager():
        """Test fake_sounddevice with custom device manager."""
        original_query_devices = sd.query_devices

        # Create custom device manager with 8 devices
        init_device_manager = devices.DeviceManager.new_basic(device_count=8)

        with patching.setup(init_device_manager) as device_manager:
            assert sd.query_devices is not original_query_devices
            assert device_manager is init_device_manager

        # Should be restored after context exit
        assert sd.query_devices is original_query_devices

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
