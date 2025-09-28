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


class TestConnect:
    @staticmethod
    async def test_not_connected():
        fake_model = model.FakeRealtimeModel()
        config = rt.RealtimeModelConfig()

        assert not fake_model.is_connected
        await fake_model.connect(config)
        assert fake_model.is_connected

    @staticmethod
    async def test_connected():
        fake_model = model.FakeRealtimeModel()
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)

        with pytest.raises(AssertionError, match="Already connected"):
            await fake_model.connect(config)

        assert fake_model.is_connected


class TestAddListener:
    @staticmethod
    def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        with pytest.raises(NotImplementedError):
            fake_model.add_listener(listener)


class TestRemoveListener:
    @staticmethod
    def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        with pytest.raises(NotImplementedError):
            fake_model.remove_listener(listener)


class TestSendEvent:
    @staticmethod
    async def test_not_connected():
        fake_model = model.FakeRealtimeModel()
        event = rt.RealtimeModelSendInterrupt()

        with pytest.raises(AssertionError, match="Not connected"):
            await fake_model.send_event(event)

    @staticmethod
    async def test_not_implemented():
        fake_model = model.FakeRealtimeModel()
        config = rt.RealtimeModelConfig()
        event = rt.RealtimeModelSendInterrupt()

        await fake_model.connect(config)

        with pytest.raises(NotImplementedError):
            await fake_model.send_event(event)


class TestClose:
    @staticmethod
    async def test_success():
        fake_model = model.FakeRealtimeModel()

        await fake_model.close()
        assert not fake_model.is_connected
        await fake_model.close()
        assert not fake_model.is_connected

    @staticmethod
    async def test_reconnect():
        fake_model = model.FakeRealtimeModel()
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)
        await fake_model.close()
        await fake_model.connect(config)
        assert fake_model.is_connected
