# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

"""Monkey patching utilities for temporarily replacing object attributes."""

import dataclasses
import logging
from typing import Any

PatchKey = tuple[int, str]


@dataclasses.dataclass(frozen=True)
class Patch:
    """Stores the original value of a patched attribute.

    Attributes:
        original: The original attribute value before patching.
    """

    original: Any


class Patcher:
    """Context manager for temporarily patching object attributes.

    Tracks all patches and automatically restores original values when exiting
    the context or when reset() is called.
    """

    def __init__(self):
        """Initialize a new Patcher instance."""
        self.__patched_obj: dict[PatchKey, Patch] = {}
        self.__target_objects: dict[int, Any] = {}

    def patched_objects(self) -> list[PatchKey]:
        """Get a sorted list of all currently patched objects.

        Returns:
            List of (object_id, attribute_name) tuples for all patches.
        """
        return sorted(self.__patched_obj.keys())

    def patch(self, target_obj: Any, name: str, replacement: Any):
        """Patch an attribute on target_obj with replacement value.

        Args:
            target_obj: The object to patch (class, module, instance, etc.)
            name: The attribute name to replace
            replacement: The new value to set

        Raises:
            AttributeError: If the attribute doesn't exist on target_obj
            ValueError: If the attribute has already been patched
        """
        key = (id(target_obj), name)

        # Fail if already patched
        if key in self.__patched_obj:
            raise ValueError(f"Attribute '{name}' on {target_obj} is already patched")

        # Fail if attribute doesn't exist
        if not hasattr(target_obj, name):
            raise AttributeError(f"'{type(target_obj).__name__}' object has no attribute '{name}'")

        # Store original value and target object reference
        original_value = getattr(target_obj, name)
        try:
            setattr(target_obj, name, replacement)
        except AttributeError:
            raise ValueError(f"Attribute '{name}' on {target_obj} is unsupported") from None
        self.__patched_obj[key] = Patch(original=original_value)
        self.__target_objects[id(target_obj)] = target_obj

    def reset(self):
        """Restore all patched attributes to their original values.

        Logs any exceptions during restoration but continues processing.
        Raises RuntimeError at the end if any attributes couldn't be restored.
        """
        failures = []

        for (obj_id, attr_name), patch in self.__patched_obj.items():
            try:
                target_obj = self.__target_objects[obj_id]
                setattr(target_obj, attr_name, patch.original)

            except Exception as e:
                error_msg = f"Failed to restore '{attr_name}' on object {obj_id}: {e}"
                logging.getLogger("fakesd.monkeypatch").error(error_msg)
                failures.append(error_msg)

        # Clear both dictionaries
        self.__patched_obj.clear()
        self.__target_objects.clear()

        if failures:
            raise RuntimeError(f"Failed to restore {len(failures)} patches: {'; '.join(failures)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()
