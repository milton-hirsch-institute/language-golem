# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0


import typing

from agents import realtime as rt


class FakeRealtimeModel(rt.RealtimeModel):
    @typing.override
    async def connect(self, options: rt.RealtimeModelConfig):
        raise NotImplementedError()

    @typing.override
    def add_listener(self, listener: rt.RealtimeModelListener):
        raise NotImplementedError()

    @typing.override
    def remove_listener(self, listener: rt.RealtimeModelListener):
        raise NotImplementedError()

    @typing.override
    async def send_event(self, event: rt.RealtimeModelSendEvent):
        raise NotImplementedError()

    @typing.override
    async def close(self):
        raise NotImplementedError()
