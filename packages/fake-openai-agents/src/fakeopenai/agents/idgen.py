# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0


class IdGenerator:
    @property
    def prefix(self) -> str:
        return self.__prefix

    def __init__(self, prefix: str):
        self.__prefix = prefix
        self.__counter = 1

    def next(self) -> str:
        next_id = f"{self.__prefix}_{self.__counter:06d}"
        self.__counter += 1
        return next_id
