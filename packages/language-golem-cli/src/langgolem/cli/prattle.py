# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0
import asyncio

import click
from langgolem.audio import asyncaudio


class EndProgram(Exception):
    """Raised when the program exited."""


@click.command()
@click.option("-i", "--input-file", type=click.File("rb"), default=None)
def prattle(input_file):
    """Have a prattle with the language golem"""
    audio_queue = asyncio.Queue[asyncaudio.RawAudio]()

    if input_file:
        queuer = asyncaudio.stream_queuer(input_file, audio_queue)
    else:
        click.secho("Audio input devices not supported.", fg="red", err=True)
        exit(1)

    async def read_queue():
        loop = asyncio.get_event_loop()
        while audio := await audio_queue.get():
            loop.run_in_executor(None, click.echo, audio.frames)

    async def queue_audio():
        await queuer
        raise EndProgram()

    async def run():
        try:
            async with asyncio.TaskGroup() as task_group:
                task_group.create_task(read_queue())
                task_group.create_task(queue_audio())
        except* EndProgram:
            pass

    asyncio.run(run())
