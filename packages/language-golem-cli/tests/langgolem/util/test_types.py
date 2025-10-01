# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import io

from langgolem.util import queues
from langgolem.util import types


def test_bytes_reader():
    def fn(br: types.BytesReader):
        pass

    fn(io.BytesIO())
    fn(queues.QueueStream(asyncio.Queue[bytes]()))
