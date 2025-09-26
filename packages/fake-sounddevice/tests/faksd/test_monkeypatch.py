# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import builtins
import logging
import os
import sys
from collections.abc import Iterator

import pytest
from fakesd.monkeypatch import Patcher


class TestPatcher:
    @staticmethod
    @pytest.fixture
    def patcher() -> Iterator[Patcher]:
        """Create a Patcher instance that is automatically cleaned up after each test."""
        patcher = Patcher()
        try:
            yield patcher
        finally:
            patcher.reset()

    class TestPatch:
        @staticmethod
        def test_patch_module(patcher):
            """Test patching a module attribute successfully."""
            patcher.patch(os, "name", "fake_os")
            assert os.name == "fake_os"
            assert patcher.patched_objects() == [(id(os), "name")]

        @staticmethod
        def test_patch_class_function(patcher):
            """Test patching a class attribute successfully."""

            class TestClass:
                def function(self):
                    pytest.fail("original function was called")

            def replacement_function(self):
                nonlocal instance
                return self is instance

            patcher.patch(TestClass, "function", replacement_function)
            assert TestClass.function is replacement_function
            assert patcher.patched_objects() == [(id(TestClass), "function")]

            instance = TestClass()
            assert instance.function() is True

        @staticmethod
        def test_patch_instance_method(patcher):
            """Test patching a method on a class successfully."""

            class TestClass:
                def method(self):
                    pytest.fail("original method was called")

            def new_method(self):
                nonlocal instance
                return self is instance

            patcher.patch(TestClass, "method", new_method)
            instance = TestClass()
            assert instance.method() is True
            assert patcher.patched_objects() == [(id(TestClass), "method")]

        @staticmethod
        def test_patch_nonexistent(patcher):
            """Test attempting to patch a non-existent attribute fails."""

            class TestClass:
                pass

            with pytest.raises(
                AttributeError, match="'type' object has no attribute 'nonexistent'"
            ):
                patcher.patch(TestClass, "nonexistent", "value")

            assert not hasattr(TestClass, "nonexistent")
            assert patcher.patched_objects() == []

        @staticmethod
        def test_patch_already_patched(patcher):
            """Test attempting to patch an already patched attribute fails."""

            class TestClass:
                attr = "original"

            patcher.patch(TestClass, "attr", "first_patch")

            patched_objects = patcher.patched_objects()

            with pytest.raises(ValueError, match="Attribute 'attr' on .* is already patched"):
                patcher.patch(TestClass, "attr", "second_patch")

            assert TestClass.attr == "first_patch"
            assert patcher.patched_objects() == patched_objects

        @staticmethod
        def test_patch_unpatchable(patcher):
            """Test patching an unpatchable property fails with ValueError."""

            class TestClass:
                @property
                def readonly_prop(self):
                    return "original_readonly"

            obj = TestClass()

            # Should fail because readonly properties can't be patched with setattr
            with pytest.raises(ValueError, match="Attribute 'readonly_prop' on .* is unsupported"):
                patcher.patch(obj, "readonly_prop", "patched_readonly")

            # Verify no patches were recorded
            assert patcher.patched_objects() == []
            assert obj.readonly_prop == "original_readonly"

    class TestReset:
        @staticmethod
        def test_reset_successful(patcher):
            """Test successful reset of all patches."""

            original_os_name = os.name
            original_sys_platform = sys.platform

            patcher.patch(os, "name", "fake_os")
            patcher.patch(sys, "platform", "fake_platform")

            patcher.reset()

            assert os.name == original_os_name
            assert sys.platform == original_sys_platform
            assert patcher.patched_objects() == []

        @staticmethod
        def test_reset_with_error(patcher, caplog):
            """Test reset when an error occurs during restoration."""

            class TestClass:
                attr = "original"

            patcher.patch(TestClass, "attr", "patched")

            # Mock setattr to raise an exception during reset
            original_setattr = setattr

            def failing_setattr(obj, name, value):
                if obj is TestClass and name == "attr":
                    raise AttributeError("can't set attribute")
                original_setattr(obj, name, value)

            builtins.setattr = failing_setattr
            try:
                with caplog.at_level(logging.ERROR, logger="fakesd.monkeypatch"):
                    with pytest.raises(RuntimeError, match="Failed to restore 1 patches"):
                        patcher.reset()
            finally:
                builtins.setattr = original_setattr

            # Check that error was logged
            assert len(caplog.records) == 1
            name, level, message = caplog.record_tuples[0]
            assert name == "fakesd.monkeypatch"
            assert level == logging.ERROR
            assert (
                message
                == f"Failed to restore 'attr' on object {id(TestClass)}: can't set attribute"
            )

            # assert "Failed to restore 'readonly_prop'" in caplog.records[0].message

    class TestPatchedObjects:
        @staticmethod
        def test_patched_objects_empty(patcher):
            """Test patched_objects returns empty list when no patches applied."""
            assert patcher.patched_objects() == []

        @staticmethod
        def test_patched_objects_populated(patcher):
            """Test patched_objects returns correct list when patches are applied."""
            patcher.patch(os, "name", "fake_os")
            patcher.patch(sys, "platform", "fake_platform")

            patched = patcher.patched_objects()
            assert len(patched) == 2
            assert (id(os), "name") in patched
            assert (id(sys), "platform") in patched

            # Verify it returns a sorted list
            assert patched == sorted(patched)
