# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import AsyncIterator
from typing import override

import pytest
from agents import realtime as rt
from fakeopenai.agents import model


class FakeRealtimeModelListener(rt.RealtimeModelListener):
    @override
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
    def test_add_new_listener():
        fake_model = model.FakeRealtimeModel()

        listener1 = FakeRealtimeModelListener()
        fake_model.add_listener(listener1)
        assert fake_model.listeners == (listener1,)

        listener2 = FakeRealtimeModelListener()
        fake_model.add_listener(listener2)
        assert fake_model.listeners == (listener1, listener2)

    @staticmethod
    def test_add_duplicate_listener():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)
        fake_model.add_listener(listener)

        assert fake_model.listeners == (listener,)


class TestRemoveListener:
    @staticmethod
    def test_remove_existing_listener():
        fake_model = model.FakeRealtimeModel()
        listener1 = FakeRealtimeModelListener()
        listener2 = FakeRealtimeModelListener()

        fake_model.add_listener(listener1)
        fake_model.add_listener(listener2)

        fake_model.remove_listener(listener1)

        assert fake_model.listeners == (listener2,)

    @staticmethod
    def test_remove_nonexistent_listener():
        fake_model = model.FakeRealtimeModel()
        listener = FakeRealtimeModelListener()

        fake_model.remove_listener(listener)

        assert fake_model.listeners == ()


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


class TestRunning:
    @staticmethod
    @pytest.fixture
    def default_agent() -> rt.RealtimeAgent:
        return rt.RealtimeAgent(name="Fake Golem", instructions="You are a fake agent")

    @staticmethod
    @pytest.fixture
    def realtime_model() -> model.FakeRealtimeModel:
        return model.FakeRealtimeModel()

    @staticmethod
    @pytest.fixture
    def realtime_runner(default_agent, realtime_model) -> rt.RealtimeRunner:
        return rt.RealtimeRunner(default_agent, model=realtime_model)

    @staticmethod
    @pytest.fixture
    async def realtime_session(realtime_runner) -> AsyncIterator[rt.RealtimeSession]:
        async with await realtime_runner.run() as session:
            yield session

    @staticmethod
    async def test_create_session(realtime_model, realtime_session):
        assert realtime_session.model == realtime_model
        assert realtime_model.is_connected
        assert realtime_model.listeners == (realtime_session,)
