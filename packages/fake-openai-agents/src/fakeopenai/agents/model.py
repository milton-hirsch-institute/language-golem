# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0


import typing

from agents import realtime as rt


class FakeRealtimeModel(rt.RealtimeModel):
    @property
    def is_connected(self) -> bool:
        return self.__is_connected

    @property
    def listeners(self) -> tuple[rt.RealtimeModelListener, ...]:
        return tuple(self.__listeners)

    def __init__(self):
        self.__is_connected = False
        self.__listeners: list[rt.RealtimeModelListener] = []

    @typing.override
    async def connect(self, options: rt.RealtimeModelConfig):
        if self.__is_connected:
            raise AssertionError("Already connected")
        self.__is_connected = True

    def add_listener(self, listener: rt.RealtimeModelListener) -> None:
        """Add a listener to the model."""
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def remove_listener(self, listener: rt.RealtimeModelListener) -> None:
        """Remove a listener from the model."""
        if listener in self.__listeners:
            self.__listeners.remove(listener)

    @typing.override
    async def send_event(self, event: rt.RealtimeModelSendEvent):
        if not self.is_connected:
            raise AssertionError("Not connected")
        raise NotImplementedError()

    @typing.override
    async def close(self):
        self.__is_connected = False
