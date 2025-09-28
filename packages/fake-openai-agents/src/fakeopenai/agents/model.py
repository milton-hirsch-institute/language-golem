# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
from typing import override

from agents import realtime as rt
from agents.realtime import model_events
from openai.types.realtime import realtime_server_event as rt_server_event


class FakeRealtimeModel(rt.RealtimeModel):
    @property
    def is_connected(self) -> bool:
        return self.__return_task is not None

    @property
    def listeners(self) -> tuple[rt.RealtimeModelListener, ...]:
        return tuple(self.__listeners)

    def __init__(self):
        self.__return_queue = asyncio.Queue[model_events.RealtimeModelEvent]()
        self.__return_task: asyncio.Task[None] | None = None
        self.__listeners: list[rt.RealtimeModelListener] = []

    @override
    async def connect(self, options: rt.RealtimeModelConfig):
        if self.is_connected:
            raise AssertionError("Already connected")
        self.__return_task = asyncio.create_task(self.__send_return_messages())

    def add_listener(self, listener: rt.RealtimeModelListener) -> None:
        """Add a listener to the model."""
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def remove_listener(self, listener: rt.RealtimeModelListener) -> None:
        """Remove a listener from the model."""
        if listener in self.__listeners:
            self.__listeners.remove(listener)

    @override
    async def send_event(self, event: rt.RealtimeModelSendEvent):
        if not self.is_connected:
            raise AssertionError("Not connected")
        raise NotImplementedError()

    @override
    async def close(self):
        if self.is_connected:
            assert self.__return_task is not None
            self.__return_task.cancel()
            try:
                await self.__return_task
            except asyncio.CancelledError:
                pass
            self.__return_task = None
            while not self.__return_queue.empty():
                self.__return_queue.get_nowait()

    def return_server_message(self, message: rt_server_event.RealtimeServerEvent):
        data = message.model_dump()
        server_message = model_events.RealtimeModelRawServerEvent(data=data)
        self.return_message(server_message)

    def return_message(self, message: model_events.RealtimeModelEvent):
        self.__return_queue.put_nowait(message)

    async def __send_return_messages(self):
        while True:
            message = await self.__return_queue.get()
            coros = [listener.on_event(message) for listener in self.__listeners]
            await asyncio.gather(*coros)
