# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import dataclasses
from collections.abc import AsyncIterator
from typing import Any

import sounddevice
from agents import realtime as rt
from langgolem.audio import devices
from langgolem.util import misc
from langgolem.util import types as langgolem_types


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

        def queue_audio():
            queue.put_nowait(audio)

        loop.call_soon_threadsafe(queue_audio)

    with devices.default_input_stream(callback):
        await asyncio.Future()


async def stream_queuer(
    stream: langgolem_types.BytesReader,
    queue: asyncio.Queue[RawAudio],
    *,
    block_size: int = 1 << 16,
):
    while block := stream.read(block_size):
        await queue.put(RawAudio(buffer=block, frames=int(len(block) / 2), time=misc.time()))


async def default_input_iterator() -> AsyncIterator[RawAudio]:
    queue = asyncio.Queue[RawAudio]()
    task = asyncio.create_task(default_input_queuer(queue))
    try:
        while True:
            yield await queue.get()
    finally:
        task.cancel()
        await task


async def audio_sender(
    session: rt.RealtimeSession, input_queue: asyncio.Queue[RawAudio], commit_size: int = 1 << 16
):
    sent_bytes = 0
    try:
        while audio := await input_queue.get():
            sent_bytes += len(audio.buffer)
            commit = bool(sent_bytes >= commit_size)
            await session.send_audio(audio.buffer, commit=commit)
    except asyncio.CancelledError:
        pass
