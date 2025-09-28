# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import typing

import pytest
from agents import realtime as rt
from fakeopenai.agents import model


class FakeRealtimeModelListener(rt.RealtimeModelListener):
    @typing.override
    async def on_event(self, event: rt.RealtimeModelEvent):
        raise NotImplementedError()


class TestFakeRealtimeModelConnect:
    @staticmethod
    async def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        config = rt.RealtimeModelConfig()

        with pytest.raises(NotImplementedError):
            await fake_model.connect(config)


class TestFakeRealtimeModelAddListener:
    @staticmethod
    def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        with pytest.raises(NotImplementedError):
            fake_model.add_listener(listener)


class TestFakeRealtimeModelRemoveListener:
    @staticmethod
    def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        with pytest.raises(NotImplementedError):
            fake_model.remove_listener(listener)


class TestFakeRealtimeModelSendEvent:
    @staticmethod
    async def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        event = rt.RealtimeModelSendInterrupt()

        with pytest.raises(NotImplementedError):
            await fake_model.send_event(event)


class TestFakeRealtimeModelClose:
    @staticmethod
    async def test_not_implemented():
        fake_model = model.FakeRealtimeModel()

        with pytest.raises(NotImplementedError):
            await fake_model.close()
