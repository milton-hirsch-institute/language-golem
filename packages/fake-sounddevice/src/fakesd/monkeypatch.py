# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import logging
from typing import Any

PatchKey = tuple[int, str]


@dataclasses.dataclass(frozen=True)
class Patch:
    original: Any


class Patcher:
    def __init__(self):
        self.__patched_obj: dict[PatchKey, Patch] = {}
        self.__target_objects: dict[int, Any] = {}

    def patched_objects(self) -> list[PatchKey]:
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
