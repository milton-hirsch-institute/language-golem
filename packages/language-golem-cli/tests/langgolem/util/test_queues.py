# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import string

import pytest
from langgolem.util import queues


class TestPopulateQueue:
    @staticmethod
    def test_hit_no_limit():
        q = asyncio.Queue[int]()
        assert queues.populate_queue(q, [1, 2, 3, 4]) == 4
        assert queues.empty_queue(q) == [1, 2, 3, 4]

    @staticmethod
    def test_hit_limit():
        q = asyncio.Queue[int](3)
        assert queues.populate_queue(q, [1, 2, 3, 4]) == 3
        assert queues.empty_queue(q) == [1, 2, 3]

    @staticmethod
    def test_existing_content():
        q = asyncio.Queue[int]()
        q.put_nowait(100)
        assert queues.populate_queue(q, [1, 2, 3, 4]) == 4
        assert queues.empty_queue(q) == [100, 1, 2, 3, 4]


class TestPopulatedQueue:
    @staticmethod
    def test_no_limit():
        q = queues.populated_queue([1, 2, 3, 4])
        assert q.maxsize == 0
        assert queues.empty_queue(q) == [1, 2, 3, 4]

    @staticmethod
    def test_has_limit():
        q = queues.populated_queue([1, 2, 3, 4], 5)
        assert q.maxsize == 5
        assert queues.empty_queue(q) == [1, 2, 3, 4]

    @staticmethod
    def test_hit_limit():
        with pytest.raises(ValueError, match="^Number items must be less than or equal to 3$"):
            queues.populated_queue([1, 2, 3, 4], 3)


class TestEmptyQueue:
    @staticmethod
    def test_empty():
        q = asyncio.Queue[int]()
        assert queues.empty_queue(q) == []
        assert q.qsize() == 0

    @staticmethod
    def test_has_content():
        q = asyncio.Queue[int]()
        q.put_nowait(1)
        q.put_nowait(2)
        q.put_nowait(3)
        assert queues.empty_queue(q) == [1, 2, 3]
        assert q.qsize() == 0


class TestQueueStream:
    @staticmethod
    @pytest.fixture
    def queue_content() -> list[bytes]:
        return []

    @staticmethod
    @pytest.fixture
    def queue(queue_content) -> asyncio.Queue:
        queue = asyncio.Queue()
        for content in queue_content:
            queue.put_nowait(content)
        return queue

    @staticmethod
    @pytest.fixture
    def stream(queue) -> queues.QueueStream:
        return queues.QueueStream(queue)

    @staticmethod
    def test_empty_queue(stream):
        assert stream.read(0) == b""
        assert stream.read(1000) == b""

    @staticmethod
    @pytest.mark.parametrize(
        "queue_content",
        [
            [
                bytes(string.ascii_letters, encoding="utf-8"),
            ]
        ],
    )
    def test_read_less_than_buffer(stream):
        assert stream.read(3) == b"abc"
        assert stream.read(3) == b"def"
        assert stream.read(3) == b"ghi"

    @staticmethod
    @pytest.mark.parametrize("queue_content", [[b"abcd", b"efgh", b"ijkl", b"mnop"]])
    def test_read_multi_buffers(stream):
        assert stream.read(3) == b"abc"
        assert stream.read(3) == b"def"
        assert stream.read(3) == b"ghi"
        assert stream.read(3) == b"jkl"
        assert stream.read(3) == b"mno"
        assert stream.read(3) == b"p"
        assert stream.read(3) == b""

    @staticmethod
    @pytest.mark.parametrize("queue_content", [[b"abcd", b"efgh", b"ijkl", b"mnop"]])
    @pytest.mark.parametrize("count", [None, -1, -2])
    def test_read_all(stream, count):
        assert stream.read(None) == b"abcdefghijklmnop"
