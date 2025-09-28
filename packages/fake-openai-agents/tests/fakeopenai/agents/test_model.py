# Copyright 2025 The Milton Hirsch Institute, B.V.
# SPDX-License-Identifier: Apache-2.0

import asyncio
from collections.abc import AsyncIterator
from typing import override

import pytest
from agents import realtime as rt
from agents.realtime import model_events
from fakeopenai.agents import model


class FakeRealtimeModelListener(rt.RealtimeModelListener):
    def __init__(self):
        self.events: list[rt.RealtimeModelEvent] = []

    @override
    async def on_event(self, event: rt.RealtimeModelEvent):
        self.events.append(event)


@pytest.fixture
async def fake_model() -> AsyncIterator[model.FakeRealtimeModel]:
    fake_model = model.FakeRealtimeModel()
    try:
        yield fake_model
    finally:
        await fake_model.close()


def assert_initial_session_events(
    created_event: model_events.RealtimeModelEvent, updated_event: model_events.RealtimeModelEvent
):
    assert isinstance(created_event, model_events.RealtimeModelRawServerEvent)
    assert created_event.type == "raw_server_event"

    assert created_event.data == {
        "event_id": "event_000001",
        "session": {
            "audio": {
                "input": {
                    "format": {"rate": 24000, "type": "audio/pcm"},
                    "noise_reduction": None,
                    "transcription": None,
                    "turn_detection": {
                        "create_response": True,
                        "idle_timeout_ms": None,
                        "interrupt_response": True,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200,
                        "threshold": 0.5,
                        "type": "server_vad",
                    },
                },
                "output": {
                    "format": {"rate": 24000, "type": "audio/pcm"},
                    "speed": 1.0,
                    "voice": "alloy",
                },
            },
            "id": "sess_000001",
            "include": None,
            "instructions": "fake-instructions",
            "max_output_tokens": None,
            "model": "gpt-realtime",
            "object": "realtime.session",
            "output_modalities": ["audio"],
            "prompt": None,
            "tool_choice": "auto",
            "tools": [],
            "tracing": None,
            "truncation": "auto",
            "type": "realtime",
        },
        "type": "session.created",
    }

    assert isinstance(updated_event, model_events.RealtimeModelRawServerEvent)
    assert updated_event.type == "raw_server_event"

    assert updated_event.data == {
        "event_id": "event_000002",
        "session": {
            "audio": {
                "input": {
                    "format": {"rate": 24000, "type": "audio/pcm"},
                    "noise_reduction": None,
                    "transcription": None,
                    "turn_detection": {
                        "create_response": True,
                        "eagerness": "auto",
                        "interrupt_response": True,
                        "type": "semantic_vad",
                    },
                },
                "output": {
                    "format": {"rate": 24000, "type": "audio/pcm"},
                    "speed": 1.0,
                    "voice": "alloy",
                },
            },
            "id": "sess_000001",
            "include": None,
            "instructions": "fake-golem-instructions",
            "max_output_tokens": None,
            "model": "gpt-realtime",
            "object": "realtime.session",
            "output_modalities": ["audio"],
            "prompt": None,
            "tool_choice": "auto",
            "tools": [],
            "tracing": None,
            "truncation": "auto",
            "type": "realtime",
        },
        "type": "session.updated",
    }


class TestConnect:
    @staticmethod
    async def test_not_connected(fake_model):
        config = rt.RealtimeModelConfig()
        listener = FakeRealtimeModelListener()
        fake_model.add_listener(listener)

        assert not fake_model.is_connected
        await fake_model.connect(config)
        assert fake_model.is_connected

        for _ in range(10):
            await asyncio.sleep(0)

        session_created, session_updated = listener.events
        assert_initial_session_events(session_created, session_updated)

    @staticmethod
    async def test_connected(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)

        with pytest.raises(AssertionError, match="Already connected"):
            await fake_model.connect(config)

        assert fake_model.is_connected


class TestAddListener:
    @staticmethod
    async def test_add_new_listener(fake_model):
        listener1 = FakeRealtimeModelListener()
        fake_model.add_listener(listener1)
        assert fake_model.listeners == (listener1,)

        listener2 = FakeRealtimeModelListener()
        fake_model.add_listener(listener2)
        assert fake_model.listeners == (listener1, listener2)

    @staticmethod
    async def test_add_duplicate_listener(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)
        fake_model.add_listener(listener)

        assert fake_model.listeners == (listener,)


class TestRemoveListener:
    @staticmethod
    async def test_remove_existing_listener(fake_model):
        listener1 = FakeRealtimeModelListener()
        listener2 = FakeRealtimeModelListener()

        fake_model.add_listener(listener1)
        fake_model.add_listener(listener2)

        fake_model.remove_listener(listener1)

        assert fake_model.listeners == (listener2,)

    @staticmethod
    async def test_remove_nonexistent_listener(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.remove_listener(listener)

        assert fake_model.listeners == ()


class TestSendEvent:
    @staticmethod
    async def test_not_connected(fake_model):
        event = rt.RealtimeModelSendInterrupt()

        with pytest.raises(AssertionError, match="Not connected"):
            await fake_model.send_event(event)

    @staticmethod
    async def test_not_implemented(fake_model):
        config = rt.RealtimeModelConfig()
        event = rt.RealtimeModelSendInterrupt()

        await fake_model.connect(config)

        with pytest.raises(NotImplementedError):
            await fake_model.send_event(event)


class TestClose:
    @staticmethod
    async def test_success(fake_model):
        await fake_model.close()
        assert not fake_model.is_connected
        await fake_model.close()
        assert not fake_model.is_connected

    @staticmethod
    async def test_reconnect(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)
        await fake_model.close()
        await fake_model.connect(config)
        assert fake_model.is_connected

    @staticmethod
    async def test_queue_cleanup(fake_model):
        config = rt.RealtimeModelConfig()

        await fake_model.connect(config)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        fake_model.return_message(test_event)
        fake_model.return_message(test_event)

        await fake_model.close()

        listener = FakeRealtimeModelListener()
        fake_model.add_listener(listener)
        await fake_model.connect(config)

        await asyncio.sleep(0)

        assert len(listener.events) == 0


class TestReturnMessage:
    @staticmethod
    async def test_multiple_listeners(fake_model):
        config = rt.RealtimeModelConfig()
        listener1 = FakeRealtimeModelListener()
        listener2 = FakeRealtimeModelListener()

        fake_model.add_listener(listener1)
        fake_model.add_listener(listener2)
        await fake_model.connect(config)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        fake_model.return_message(test_event)

        for _ in range(10):
            await asyncio.sleep(0)

        assert len(listener1.events) == 3  # session.created + test_event
        assert len(listener2.events) == 3  # session.created + test_event
        assert_initial_session_events(listener1.events[0], listener1.events[1])
        assert listener1.events[2] == test_event
        assert_initial_session_events(listener2.events[0], listener2.events[1])
        assert listener2.events[2] == test_event

    @staticmethod
    async def test_not_connected(fake_model):
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)

        test_event = model_events.RealtimeModelRawServerEvent(data={"type": "test"})
        with pytest.raises(AssertionError, match="Model is not connected"):
            fake_model.return_message(test_event)

        await asyncio.sleep(0.01)

        assert len(listener.events) == 0

    @staticmethod
    async def test_connect_after_adding_events(fake_model):
        config = rt.RealtimeModelConfig()
        listener = FakeRealtimeModelListener()

        fake_model.add_listener(listener)

        test_event = model_events.RealtimeModelTurnStartedEvent()
        with pytest.raises(AssertionError, match="Model is not connected"):
            fake_model.return_message(test_event)

        await asyncio.sleep(0)
        assert listener.events == []

        await fake_model.connect(config)
        for _ in range(10):
            await asyncio.sleep(0)

        created_event, updated_event = listener.events
        assert_initial_session_events(created_event, updated_event)


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

    @staticmethod
    async def test_send_audio(realtime_session):
        with pytest.raises(NotImplementedError):
            await realtime_session.send_audio(b"realtime-audio")
