# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import dataclasses
from collections.abc import AsyncIterator
from typing import Any

import sounddevice
from langgolem.audio import devices


@dataclasses.dataclass
class RawAudio:
    buffer: bytes
    frames: int
    time: float


async def default_input_queuer(queue: asyncio.Queue[RawAudio]):
    loop = asyncio.get_event_loop()

    def callback(
        buffer: Any, frame_count: int, time: devices.Time, status: sounddevice.CallbackFlags
    ):
        audio = RawAudio(bytes(buffer), frame_count, time.inputBufferAdcTime)
        loop.call_soon_threadsafe(queue.put_nowait, audio)

    with devices.default_input_stream(callback):
        await asyncio.Future()


async def default_input_iterator() -> AsyncIterator[RawAudio]:
    queue = asyncio.Queue[RawAudio]()
    task = asyncio.create_task(default_input_queuer(queue))
    try:
        while True:
            yield await queue.get()
    finally:
        task.cancel()
        await task
