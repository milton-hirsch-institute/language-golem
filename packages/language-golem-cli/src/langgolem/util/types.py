# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import typing


class BytesReader(typing.Protocol):
    def read(self, count: int | None = -1, /) -> bytes: ...
