# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0


import typing

from agents import realtime as rt


class FakeRealtimeModel(rt.RealtimeModel):
    @property
    def is_connected(self) -> bool:
        return self.__is_connected

    def __init__(self):
        self.__is_connected = False

    @typing.override
    async def connect(self, options: rt.RealtimeModelConfig):
        if self.__is_connected:
            raise AssertionError("Already connected")
        self.__is_connected = True

    @typing.override
    def add_listener(self, listener: rt.RealtimeModelListener):
        raise NotImplementedError()

    @typing.override
    def remove_listener(self, listener: rt.RealtimeModelListener):
        raise NotImplementedError()

    @typing.override
    async def send_event(self, event: rt.RealtimeModelSendEvent):
        if not self.is_connected:
            raise AssertionError("Not connected")
        raise NotImplementedError()

    @typing.override
    async def close(self):
        self.__is_connected = False
