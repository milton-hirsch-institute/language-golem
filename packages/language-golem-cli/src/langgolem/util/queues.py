# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
from collections.abc import Sequence


def populate_queue[T](queue: asyncio.Queue[T], items: Sequence[T]) -> int:
    count = 0
    for item in items:
        try:
            queue.put_nowait(item)
        except asyncio.QueueFull:
            break
        else:
            count += 1
    return count


def populated_queue[T](items: Sequence[T], maxsize=0) -> asyncio.Queue[T]:
    if maxsize != 0 and len(items) > maxsize:
        raise ValueError(f"Number items must be less than or equal to {maxsize}")
    queue = asyncio.Queue[T](maxsize=maxsize)
    populate_queue(queue, items)
    return queue


def empty_queue[T](queue: asyncio.Queue[T]) -> list[T]:
    result = []
    while True:
        try:
            result.append(queue.get_nowait())
        except asyncio.QueueEmpty:
            break
    return result


class QueueStream:
    def __init__(self, queue: asyncio.Queue[bytes]):
        self.__queue = queue
        self.__current_bytes = b""
        self.__offset = 0

    def read(self, count: int | None = -1, /) -> bytes:
        if count is not None and count < 0:
            count = None
        result = bytearray()
        while count is None or count > 0:
            if self.__offset >= len(self.__current_bytes):
                self.__offset = 0
                try:
                    self.__current_bytes = self.__queue.get_nowait()
                except asyncio.QueueEmpty:
                    self.__current_bytes = b""
                    break
            if count is None:
                next_bytes = self.__current_bytes[self.__offset :]
            else:
                next_bytes = self.__current_bytes[self.__offset : self.__offset + count]
            self.__offset += len(next_bytes)
            result.extend(next_bytes)
            if count is not None:
                count -= len(next_bytes)
        return bytes(result)
