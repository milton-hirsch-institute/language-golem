# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from fakeopenai.agents import idgen


class TestIdGenerator:
    @staticmethod
    def test_prefix():
        generator = idgen.IdGenerator("test")

        assert generator.prefix == "test"

    @staticmethod
    def test_next():
        generator1 = idgen.IdGenerator("test1")

        assert generator1.next() == "test1_000001"
        assert generator1.next() == "test1_000002"
        assert generator1.next() == "test1_000003"

        generator1 = idgen.IdGenerator("test2")

        assert generator1.next() == "test2_000001"
        assert generator1.next() == "test2_000002"
