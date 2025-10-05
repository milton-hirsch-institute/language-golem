# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio

import pytest
from fakesd import waves
from langgolem.audio import asyncaudio


@pytest.fixture(autouse=True)
def enable_fake_soundevice(fake_sd):
    pass


async def test_default_input_queuer():
    queue = asyncio.Queue[asyncaudio.RawAudio]()
    task = asyncio.create_task(asyncaudio.default_input_queuer(queue))
    audio_records: list[asyncaudio.RawAudio] = []

    try:
        while True:
            next_record = await queue.get()
            if next_record.frames == 0:
                break
            else:
                audio_records.append(next_record)
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        else:
            pytest.fail("Queue task was not cancelled")

    assert len(audio_records) == 375
    for index, record in enumerate(audio_records):
        assert record.frames == 128
        assert record.time == index / 2 / 24000.0

    all_sound = b"".join(r.buffer for r in audio_records)
    assert all_sound == waves.create_sawtooth_wave(0.1, 2.0, 24000.0, 2)


async def test_default_input_iterator():
    audio_records: list[asyncaudio.RawAudio] = []

    async for audio_record in asyncaudio.default_input_iterator():
        if audio_record.frames == 0:
            break
        audio_records.append(audio_record)

    assert len(audio_records) == 375
    for index, record in enumerate(audio_records):
        assert record.frames == 128
        assert record.time == index / 2 / 24000.0

    all_sound = b"".join(r.buffer for r in audio_records)
    assert all_sound == waves.create_sawtooth_wave(0.1, 2.0, 24000.0, 2)


async def test_audio_sender(realtime_session, realtime_model):
    queue = asyncio.Queue[asyncaudio.RawAudio]()

    task = asyncio.create_task(asyncaudio.audio_sender(realtime_session, queue, commit_size=7))

    async def do_test():
        try:
            # To small to commit
            await queue.put(asyncaudio.RawAudio(buffer=b"block1", frames=6, time=0.0))
            for _ in range(10):
                await asyncio.sleep(0)
            assert realtime_model.pending_audio == b"block1"
            assert realtime_model.committed_audio == b""

            # Passes the commit boundary
            await queue.put(asyncaudio.RawAudio(buffer=b"block2", frames=6, time=0.0))
            for _ in range(10):
                await asyncio.sleep(0)
            assert realtime_model.pending_audio == b""
            assert realtime_model.committed_audio == b"block1block2"
        finally:
            task.cancel()

    await asyncio.gather(task, do_test())
