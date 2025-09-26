# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import types

import fakesd


def test_no_modules():
    """Test that all exported symbols are not modules."""
    for name in fakesd.__all__:
        symbol = getattr(fakesd, name)
        assert not isinstance(symbol, types.ModuleType), f"{name} should not be a module"


def test_all_from_fakesd():
    """Test that all exported symbols are defined within the fakesd package."""
    for name in fakesd.__all__:
        symbol = getattr(fakesd, name)
        module = getattr(symbol, "__module__", None)
        if module is not None:
            assert module.startswith("fakesd."), (
                f"{name} should be from fakesd package, but is from {module}"
            )
